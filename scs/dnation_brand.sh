#!/bin/bash
# Modify favicon
sed -i 's/\[\[.AppTitle\]\]/SCS/g' /usr/share/grafana/public/views/index.html
sed -i 's/\[\[.AppTitle\]\]/SCS/g' /usr/share/grafana/public/views/index-template.html
sed -i 's/\[\[.FavIcon\]\]/https:\/\/scs.community\/assets\/favicon-32x32-c5b260bd36bab2cb0496cec647907efc38ca4ac5cb5c978603405fe682da762b16d3b21e997fc85c1c76db4e4bae08787a9a9cbfeb38c7b796ea6de38011953b.png/g' /usr/share/grafana/public/views/index.html
#Modify logp
sed -i 's@public/img/grafana_icon.svg@public/img/scs_logo.svg@g' /usr/share/grafana/public/build/*.*
#Modify app title
sed -i 's/"AppTitle","Grafana"/"AppTitle","SCS"/g' /usr/share/grafana/public/build/*.*
sed -i "s/static AppTitle = 'Grafana'/static AppTitle = 'SCS'/g" /usr/share/grafana/public/build/*.*
#Modify welcome message
sed -i 's/Welcome to Grafana/SCS Observer - powered by dNation Kubernetes Monitoring/g' /usr/share/grafana/public/build/*.*
#Modify the docs
sed -i 's@https:cd //grafana.com/docs/grafana/latest/?utm_source=grafana_footer@https://github.com/dNationCloud/kubernetes-monitoring@g' /usr/share/grafana/public/build/*.*