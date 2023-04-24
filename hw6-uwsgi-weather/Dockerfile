FROM centos:7

RUN yum install -y epel-release \
    && yum install -y python3-devel nginx gcc \
    && yum -y clean all \
    && pip3 install uwsgi

WORKDIR /srv/ip2weather

COPY ip2weather .

EXPOSE 80

ENTRYPOINT ["uwsgi", "--http", ":80", "--wsgi-file", "ip2w.py"]