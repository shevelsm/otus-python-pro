FROM centos:7

RUN yum install -y epel-release \
    && yum install -y python3-devel nginx gcc \
    && yum -y clean all \
    && pip3 install uwsgi requests

WORKDIR /srv/ip2w

COPY ip2w .

EXPOSE 9090

ENTRYPOINT ["uwsgi", "ip2w.ini"]