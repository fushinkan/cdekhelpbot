# Базовый образ
FROM alpine:latest

# Устанавливаем необходимые пакеты
RUN apk add --no-cache bash postgresql-client

# Копируем скрипт бэкапа в контейнер
COPY backup.sh /backup.sh
RUN chmod +x /backup.sh

# Устанавливаем рабочую директорию (не обязательно, но удобно)
WORKDIR /backups

# Запускаем скрипт при старте контейнера
CMD ["sh", "/backup.sh"]
