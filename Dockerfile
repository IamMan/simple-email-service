FROM lambci/lambda:build-python3.6

#RUN yum install -y yum-plugin-ovl
RUN yum clean all && \
    yum update -y && \
    yum -y install yum-plugin-ovl

RUN touch /var/lib/rpm/* && yum install -y unixODBC unixODBC-devel

#RUN ACCEPT_EULA=Y yum install msodbcsql
RUN touch /var/lib/rpm/* && yum -y install freetds freetds-devel

#https://github.com/moby/moby/issues/10180
