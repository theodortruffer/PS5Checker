FROM python:3.6
ENV TZ="Africa/Lusaka"

# app
COPY ./app /opt/app
RUN pip3 install -r /opt/app/requirements.txt

# cronjob
RUN apt-get update \
    && apt-get install -y cron \
    && apt-get autoremove -y
COPY ./cronpy /etc/cron.d/cronpy
RUN crontab /etc/cron.d/cronpy
RUN touch /var/log/cron.log

# entrypoint script
COPY ps5-py-entrypoint /usr/local/bin/ps5-py-entrypoint
# run cronjob in foreground (logs will be sent to stdout)
ENTRYPOINT ["/usr/local/bin/ps5-py-entrypoint"]
CMD cron && tail -f /var/log/cron.log
