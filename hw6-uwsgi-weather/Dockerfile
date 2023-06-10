FROM centos:7

RUN yum install -y epel-release \
    && yum install -y python3-devel nginx gcc rpm-build\
    && yum -y clean all \
    && pip3 install uwsgi requests

WORKDIR /srv/ip2w

COPY . .

# Change nginx.conf
RUN  cp /srv/ip2w/nginx_ip2w.conf /etc/nginx/conf.d/nginx_ip2w.conf \
 && sed -i 's:default_server::' /etc/nginx/nginx.conf \
 && cp /srv/ip2w/ip2w/config_ip2w.json /usr/local/etc/config_ip2w.json \
 && cp /srv/ip2w/ip2w/ip2w.py /usr/local/bin/ip2w.py \
 && mkdir /run/uwsgi

EXPOSE 80

ENTRYPOINT /usr/sbin/nginx \
 && /bin/bash 