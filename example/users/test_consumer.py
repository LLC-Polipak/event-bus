"""Tests for event bus consumer configuration and idle mode."""

# ruff: noqa: S101

import multiprocessing
import os
import signal
import sys
from unittest.mock import Mock, patch

import pytest
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.test import Client, override_settings

from django_event_bus.consumer import start_consumer, wait_until_stopped
from django_event_bus.settings import get_consumer_selection, get_event_bus_config


def run_signal_wait_in_child(ready_connection) -> None:
    """Run idle wait in a child and report when signal handlers are installed."""
    from django_event_bus import consumer as consumer_module

    original_signal = consumer_module.signal.signal

    def install_and_report(signum, handler):
        previous = original_signal(signum, handler)
        if signum == signal.SIGINT:
            ready_connection.send(True)
        return previous

    consumer_module.signal.signal = install_and_report
    try:
        consumer_module.wait_until_stopped()
    finally:
        ready_connection.close()


def event_bus_settings(**overrides):
    """Return the example configuration with selected values replaced."""
    return {**settings.EVENT_BUS, **overrides}


@override_settings(EVENT_BUS={})
def test_global_consumer_flag_defaults_to_enabled() -> None:
    """Enable the consumer when the global flag is absent."""
    assert get_event_bus_config()['CONSUMER_ENABLED'] is True


@patch('django_event_bus.consumer.threading.main_thread')
@patch('django_event_bus.consumer.threading.current_thread')
def test_consumer_cannot_run_in_background_thread(current_thread, main_thread) -> None:
    """Reject consumer startup outside the main thread."""
    current_thread.return_value = Mock(name='background_thread')
    main_thread.return_value = Mock(name='main_thread')

    with pytest.raises(RuntimeError, match='must run in the main thread'):
        start_consumer()


@override_settings(
    EVENT_BUS={
        'CONSUMER_ENABLED': True,
        'CONSUMERS': [
            {'source': 'source', 'routing_key': 'event', 'handler': 'handler'},
        ],
    }
)
@patch('django_event_bus.consumer.import_string')
@patch('django_event_bus.consumer.get_event_bus')
def test_enabled_consumer_creates_and_runs_bus(get_bus, import_string) -> None:
    """Create the bus and run subscriptions when globally enabled."""
    bus = get_bus.return_value
    handler = import_string.return_value

    start_consumer()

    get_bus.assert_called_once_with()
    import_string.assert_called_once_with('handler')
    bus.subscribe.assert_called_once_with('source', 'event', handler)
    bus.run.assert_called_once_with()


@override_settings(
    EVENT_BUS={
        'CONSUMER_ENABLED': False,
        'CONSUMERS': [{'handler': 'must.not.be.imported'}],
    }
)
@patch('django_event_bus.consumer.wait_until_stopped')
@patch('django_event_bus.consumer.import_string')
@patch('django_event_bus.consumer.get_event_bus')
def test_disabled_consumer_waits_without_creating_bus(
    get_bus, import_string, wait, caplog
) -> None:
    """Avoid connections and handler imports when globally disabled."""
    caplog.set_level('INFO', logger='django_event_bus.consumer')
    start_consumer()

    get_bus.assert_not_called()
    import_string.assert_not_called()
    wait.assert_called_once_with()
    assert 'Event bus consumer is disabled' in caplog.messages


@pytest.mark.parametrize('enabled_value', [None, 0, 1, 'true'])
def test_subscription_enabled_must_be_bool(enabled_value) -> None:
    """Reject non-boolean subscription flags."""
    config = {
        'CONSUMER_ENABLED': True,
        'CONSUMERS': [{'enabled': enabled_value}],
    }

    with pytest.raises(ImproperlyConfigured, match=r"\['enabled'\] must be a bool"):
        get_consumer_selection(config)


@pytest.mark.parametrize('enabled_value', [None, 0, 1, 'true'])
def test_global_enabled_must_be_bool(enabled_value) -> None:
    """Reject non-boolean global consumer flags."""
    with pytest.raises(ImproperlyConfigured, match='CONSUMER_ENABLED'):
        get_consumer_selection({'CONSUMER_ENABLED': enabled_value, 'CONSUMERS': []})


def test_consumers_must_be_a_list() -> None:
    """Reject non-list subscription collections."""
    with pytest.raises(ImproperlyConfigured, match='CONSUMERS'):
        get_consumer_selection(
            {'CONSUMER_ENABLED': True, 'CONSUMERS': {'handler': 'handler'}}
        )


@pytest.mark.parametrize('missing_field', ['source', 'routing_key', 'handler'])
def test_enabled_subscription_requires_all_fields(missing_field) -> None:
    """Reject enabled subscriptions with an absent required field."""
    consumer = {
        'source': 'source',
        'routing_key': 'event',
        'handler': 'handler',
    }
    consumer.pop(missing_field)

    with pytest.raises(ImproperlyConfigured, match=missing_field):
        get_consumer_selection({'CONSUMER_ENABLED': True, 'CONSUMERS': [consumer]})


@override_settings(
    EVENT_BUS={
        'CONSUMERS': [
            {'enabled': False},
            {'source': 'source', 'routing_key': 'event', 'handler': 'handler'},
        ],
    }
)
@patch('django_event_bus.consumer.wait_until_stopped')
@patch('django_event_bus.consumer.import_string')
@patch('django_event_bus.consumer.get_event_bus')
def test_mixed_subscriptions_register_only_enabled(
    get_bus, import_string, wait, caplog
) -> None:
    """Skip disabled subscriptions and default missing enabled to true."""
    caplog.set_level('INFO', logger='django_event_bus.consumer')
    bus = get_bus.return_value
    handler = import_string.return_value

    start_consumer()

    wait.assert_not_called()
    import_string.assert_called_once_with('handler')
    bus.subscribe.assert_called_once_with('source', 'event', handler)
    bus.run.assert_called_once_with()
    assert 'Skipping disabled event consumer: <unspecified>' in caplog.messages
    assert 'Starting event bus consumer with 1 subscription(s)' in caplog.messages


@override_settings(EVENT_BUS={'CONSUMERS': [{'enabled': False}]})
@patch('django_event_bus.consumer.wait_until_stopped')
@patch('django_event_bus.consumer.import_string')
@patch('django_event_bus.consumer.get_event_bus')
def test_all_disabled_subscriptions_wait_without_bus(
    get_bus, import_string, wait, caplog
) -> None:
    """Wait without connecting when every subscription is disabled."""
    caplog.set_level('INFO', logger='django_event_bus.consumer')
    start_consumer()

    get_bus.assert_not_called()
    import_string.assert_not_called()
    wait.assert_called_once_with()
    assert 'No enabled event bus consumers are configured' in caplog.messages


@patch('django_event_bus.consumer.threading.Event')
@patch('django_event_bus.consumer.signal.signal')
def test_idle_wait_finishes_on_termination_signal(set_signal, event_class) -> None:
    """Wake idle mode when its installed signal handler receives SIGTERM."""
    stop_event = event_class.return_value
    installed_handlers = {}
    previous_handler = Mock()

    def remember_handler(signum, handler):
        installed_handlers.setdefault(signum, handler)
        return previous_handler

    set_signal.side_effect = remember_handler
    stop_event.wait.side_effect = lambda: installed_handlers[signal.SIGTERM](
        signal.SIGTERM, None
    )

    wait_until_stopped()

    stop_event.set.assert_called_once_with()
    assert set_signal.call_count == 4


@pytest.mark.parametrize('signum', [signal.SIGTERM, signal.SIGINT])
@patch('django_event_bus.consumer.threading.Event')
@patch('django_event_bus.consumer.signal.signal')
def test_each_shutdown_signal_wakes_idle_wait(set_signal, event_class, signum) -> None:
    """Install working handlers for both supported shutdown signals."""
    stop_event = event_class.return_value
    installed_handlers = {}

    def remember_handler(installed_signum, handler):
        installed_handlers.setdefault(installed_signum, handler)
        return Mock()

    set_signal.side_effect = remember_handler
    stop_event.wait.side_effect = lambda: installed_handlers[signum](signum, None)

    wait_until_stopped()

    stop_event.set.assert_called_once_with()


@pytest.mark.skipif(sys.platform == 'win32', reason='POSIX signal semantics required')
def test_idle_process_exits_cleanly_on_sigterm() -> None:
    """Exit a real idle child process cleanly after receiving SIGTERM."""
    context = multiprocessing.get_context('fork')
    parent_connection, child_connection = context.Pipe(duplex=False)
    process = context.Process(
        target=run_signal_wait_in_child,
        args=(child_connection,),
    )
    process.start()
    child_connection.close()
    try:
        assert parent_connection.poll(5), 'Child did not install signal handlers'
        assert parent_connection.recv() is True
        os.kill(process.pid, signal.SIGTERM)
        process.join(5)
        assert process.exitcode == 0
    finally:
        parent_connection.close()
        if process.is_alive():
            process.kill()
            process.join()


@override_settings(EVENT_BUS={'CONSUMER_ENABLED': False, 'CONSUMERS': []})
def test_registry_http_api_works_with_disabled_consumer(client: Client) -> None:
    """Keep the registry API independent of consumer state."""
    response = client.get('/api/v1/events/')

    assert response.status_code == 200
    assert response.json()


@override_settings(EVENT_BUS={'CONSUMER_ENABLED': False})
@patch('django_event_bus.client.EventBus')
def test_publisher_bus_creation_ignores_consumer_flag(event_bus) -> None:
    """Keep the public event bus client available for publishing."""
    from django_event_bus.client import get_event_bus

    assert get_event_bus() is event_bus.return_value
    event_bus.assert_called_once()
