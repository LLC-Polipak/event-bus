#!/bin/sh
set -e

# путь к compose (на уровень выше)
COMPOSE_FILE="$(dirname "$0")/../docker-compose.yml"

USER_NAME=$1
PASSWORD=$2
SERVICE_NAME=$3
VHOST=${4:-/dev}
EXCHANGE=${5:-events}

if [ -z "$USER_NAME" ] || [ -z "$PASSWORD" ] || [ -z "$SERVICE_NAME" ]; then
  echo "Usage: ./create_user.sh <user> <password> <service_name> [vhost] [exchange]"
  exit 1
fi

echo "🚀 Using compose file: $COMPOSE_FILE"
echo "🚀 Creating user: $USER_NAME"

exec_rabbit() {
  docker compose -f "$COMPOSE_FILE" exec -T event-bus-rabbitmq rabbitmqctl "$@"
}

# создаём пользователя или обновляем пароль
if exec_rabbit list_users | grep -q "^$USER_NAME"; then
  echo "🔄 User exists, updating password..."
  exec_rabbit change_password "$USER_NAME" "$PASSWORD"
else
  exec_rabbit add_user "$USER_NAME" "$PASSWORD"
fi

# права
exec_rabbit set_permissions -p "$VHOST" "$USER_NAME" \
  "^(${SERVICE_NAME}\..*|${EXCHANGE})$" \
  "^(${EXCHANGE}|${SERVICE_NAME}\..*)" \
  "^(${EXCHANGE}|${SERVICE_NAME}\..*)"

# topic permissions
exec_rabbit set_topic_permissions -p "$VHOST" "$USER_NAME" \
  "$EXCHANGE" \
  "^${SERVICE_NAME}\..*" \
  "^${SERVICE_NAME}\..*"

echo "✅ User $USER_NAME configured"
