#!/bin/sh

# Проверка переменных окружения
if [ -z "$DB_USER" ] || [ -z "$DB_PASS" ] || [ -z "$DB_NAME" ]; then
  echo "Ошибка: не заданы переменные DB_USER, DB_PASS или DB_NAME"
  exit 1
fi

wait_for_db() {
  until PGPASSWORD=$DB_PASS pg_isready -h db -U $DB_USER -d $DB_NAME > /dev/null 2>&1; do
    echo "Ждём поднятия базы..."
    sleep 3
  done
}

wait_for_db

# Функция бэкапа
run_backup() {
  FILE="/backups/${DB_NAME}_backup_$(date +%Y-%m-%d).sql"
  echo "Создаём бэкап: $FILE"
  PGPASSWORD=$DB_PASS pg_dump -h db -U $DB_USER -d $DB_NAME > "$FILE"
  
  # Оставляем только последние 5 файлов
  ls -1t /backups/${DB_NAME}_backup_*.sql | tail -n +6 | xargs -r rm --
}

# Если передан аргумент "now", запускаем бэкап сразу
if [ "$1" = "now" ]; then
  run_backup
else
  # Создаём cron-задание еженедельного бэкапа
  echo "0 2 * * 1 /backup.sh now" > /etc/crontabs/root
  crond -f -L /var/log/cron.log
fi
