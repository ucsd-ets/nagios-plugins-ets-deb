helloworld:
	mkdir -p output
	gcc check_mem.c -o output/check_mem

install: helloworld
	install -m 0755 check_mem /usr/lib64/nagios/plugins
