# Catalog-App

This is one of Udacity's Full Stack Web Developer Nanodegree Program 's projects using Python and Flask. 
The project involves displaying a catalog in which items can be viewed, added, edited and deleted. More so JSON endpoints are available per catalog or per any chosen catagory.

### To run the project:

1. Have [Vagrant](https://www.vagrantup.com/), [Visual Box](https://www.virtualbox.org/wiki/Download_Old_Builds_5_1) and a [VM Configuration](https://s3.amazonaws.com/video.udacity-data.com/topher/2018/April/5acfbfa3_fsnd-virtual-machine/fsnd-virtual-machine.zip) installed.
2. Being inside the VM Configuration folder, get the virtual machine working by running in the terminal ```vagrant up``` and log in with ```vagrant ssh```.


### To create the database:
Inside the ```vagrant``` folder run ```python3 /vagrant/catalog/catalog.py``` in the terminal to see the results. Optionally, to populate the database run ```python3 /vagrant/catalog/database.py```

### To run the application
Run ```python3 /vagrant/catalog/application.py``` and open your localhost browser on port 8000.

### Endpoints

* Catalog page: ```/``` or ```/catalog```
* Category page: ```/catalog/<category_name>```
* Item page: ```/catalog/<category_name>/<item_title>```
* Add item: ```/catalog/new```
* Edit item: ```/catalog/<category_name>/<item_title>/edit```
* Delete item: ```/catalog/<category_name>/<item_title>/delete```
* Catalog JSON: ```/catalog/JSON```
* Category JSON: ```/catalog/<category_name>/JSON```
* Login: ```/login```
* Logout: ```/gdisconnect```