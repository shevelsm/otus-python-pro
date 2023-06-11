FROM centos:7

RUN yum install -y epel-release \
    && yum install -y python3-devel nginx gcc git rpm-build\
    && yum -y clean all \
    && pip3 install uwsgi requests

WORKDIR /srv

RUN git clone http://github.com/shevelsm/otus-python-pro

# Change nginx.conf
RUN  cp /srv/otus-python-pro/hw6-uwsgi-weather/nginx_ip2w.conf /etc/nginx/conf.d/nginx_ip2w.conf \
 && sed -i 's:default_server::' /etc/nginx/nginx.conf \
 && cp /srv/otus-python-pro/hw6-uwsgi-weather/ip2w/ip2w.ini /usr/local/etc/ip2w.ini \
 && cp /srv/otus-python-pro/hw6-uwsgi-weather/ip2w/ip2w.py /usr/local/bin/ip2w.py \
 && mkdir /run/uwsgi

EXPOSE 80

ENTRYPOINT ["/bin/bash"]