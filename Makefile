#BRANCH=$(shell git branch | grep '^*' | cut -d' ' -f2)
BRANCH=$(shell git branch | grep '^*' | cut -d' ' -f2)

#DYNAMIC_CONTENT=content/media/images/blog/2012/openstack-swift-storage.png
#DYNAMIC_CONTENT+=content/media/images/blog/2012/openstack-swift-replication.png
DYNAMIC_CONTENT=
#DYNAMIC_CONTENT=content/media/images/talks/CeilometerPlusHeatEqualsAlarming-OpenStackIcehouseSummit.png
#DYNAMIC_CONTENT+=content/media/images/talks/ceilometer-to-telemetry.png

clean-web:
	rm -rf ../deploy-web-$(BRANCH).albertdelafuente.com
	rm -rf content/blog/tags

clean-local:
	rm -rf ../deploy-local-$(BRANCH).albertdelafuente.com
	rm -rf content/blog/tags

clean-devel:
	rm -rf ../deploy-devel-$(BRANCH).albertdelafuente.com
	rm -rf content/blog/tags

deploy-web: site-web.yaml clean-web $(DYNAMIC_CONTENT)
	# I don't know how to refactor this into variables, like:
	# DEPLOY_DIR="../deploy-web-$(BRANCH).albertdelafuente.com"
	# This is very smelly! =(, no me gusta!
	find content/ -maxdepth 1 -type l -delete
	hyde -x gen -c site-web.yaml -d ../deploy-web-$(BRANCH).albertdelafuente.com

deploy-local: site-local.yaml clean-local $(DYNAMIC_CONTENT)
	ln -sf ~/Dropbox/appdata/hydesite/private ./content
	hyde -x gen -c site-local.yaml -d ../deploy-local-$(BRANCH).albertdelafuente.com

deploy-devel: site-devel.yaml clean-devel $(DYNAMIC_CONTENT)
	find content/ -maxdepth 1 -type l -delete
	hyde -x gen -c site-devel.yaml -d ../deploy-devel-$(BRANCH).albertdelafuente.com

run-web: deploy-web
	cd ../deploy-web-$(BRANCH).albertdelafuente.com && python -m SimpleHTTPServer
	# Really I wish I could use that but it's way too buggy. It keeps
	# regenerating the web site for fucking ever
	# hyde serve -p 8080

run-local: deploy-local
	cd ../deploy-local-$(BRANCH).albertdelafuente.com && python -m SimpleHTTPServer

run-devel: deploy-devel
	cd ../deploy-devel-$(BRANCH).albertdelafuente.com && python -m SimpleHTTPServer

test-web-compile: clean-web deploy-web
	cd ../deploy-web-$(BRANCH).albertdelafuente.com; \
	../hydesite/scripts/travis-push-github.sh

pub: deploy
	if [ "$(BRANCH)" = "master" ]; then \
		if ! git status | egrep -q '^nothing to commit.*working directory clean'; then echo Untracked files, not pushing && exit 1; fi; \
		echo "==> RSYNC TO PROD"; \
		rsync -Pavz --delete deploy/ albertdelafuente.com:/var/www/albertdelafuente.com/; \
	else \
		echo "==> RSYNC TO DEV"; \
		rsync -Pavz --delete deploy/ albertdelafuente.com:/var/www/devel.albertdelafuente.com/; \
	fi

#content/media/images/blog/2012/openstack-swift-storage.png: content/blog/2012/openstack-swift-storage.ditaa
#	ditaa --overwrite $< $@

#content/media/images/blog/2012/openstack-swift-replication.png: content/blog/2012/openstack-swift-replication.ditaa
#	ditaa --overwrite $< $@


content/media/images/talks/%.png: content/talks/%.pdf
	convert $<[0] $@
	pngcrush -ow $@

pngcrush:
	find content -name '*.png' -exec pngcrush -ow {} \;

.PHONY: clean-web run-web pub pngcrush
