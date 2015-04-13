
from fabric.api import *
from fabric.contrib.files import exists
from fabtools.vagrant import vagrant
from fabtools import deb, require, fabtools
from getpass import getpass

@task
def setup():
    db_user = prompt("Enter your db username:", default="databaseuser")
    db_password = prompt("Enter your db password:", default="wassup89")
    setup_geo = prompt("Setup geospatial libraries?", default=False)
    compile_geo = prompt("Compile the geospatial libraries?", default=False)

    run("sudo apt-get update")
    try:
        run('ln -s /vagrant ~/.')
    except:
        run('echo "linked file already exists"')

    sudo("locale-gen en_US.UTF-8")
    sudo("dpkg-reconfigure locales")
    sudo("""sh -c "echo 'LC_ALL=en_US.UTF-8\nLANG=en_US.UTF-8' >> /etc/default/locale" """)
    
    require.deb.packages([
        'build-essential',
        'git',
        'python-dev',       
        'python-pip',
    
        'nginx',
        'vim',
        'ipython',

        'libpq-dev', #postgres
        'postgresql',
        'postgresql-contrib',
        'python-psycopg2', #dont forget pip install psycopg2
        
    ])
    sudo("pip install virtualenv")
    run('virtualenv env')
    with fabtools.python.virtualenv('/home/vagrant/env'):
            run("pip install -r /vagrant/conf/requirements.pip")

    sudo("echo 'local all postgres trust' | sudo tee -a /etc/postgresql/9.3/main/pg_hba.conf")
    sudo("echo 'local all all trust' | sudo tee -a /etc/postgresql/9.3/main/pg_hba.conf")
    sudo("service postgresql restart")

    setup_postgresql(dbu=db_user, password=db_password, geo=setup_geo, compile_pkgs=compile_geo)

@task
def setup_postgresql(dbu="databasedbu", password="md56e768dc178fc80686d18b76a6e588428", geo=False, compile_pkgs=False):
    if geo:
        setup_geodjango(compile_pkgs=compile_pkgs)
    else:
        with settings(warn_only=True):
            run("sudo -u postgres createdb -E UTF8 -T template0 --locale=en_US.utf-8 template_postgis")
            run("""sudo -u postgres psql -c "CREATE ROLE %s WITH ENCRYPTED PASSWORD '%s' NOSUPERUSER CREATEDB NOCREATEROLE INHERIT LOGIN;" """ % (dbu, password))
            run("sudo -u postgres createdb -T template_postgis -O %s %s" % (dbu, password))
    
        

@task
def setup_geodjango(compile_pkgs=False):
    sudo("sh -c 'echo 'deb http://apt.postgresql.org/pub/repos/apt trusty-pgdg main' >> /etc/apt/sources.list'")
    run("wget --quiet -O - http://apt.postgresql.org/pub/repos/apt/ACCC4CF8.asc | sudo apt-key add -")
    deb.update_index(quiet=False)
    
    require.deb.packages([
    'build-essential',
    'git',
    'python-dev',       

    'libpq-dev', #postgres
    'postgresql',

    'postgresql-9.3-postgis-2.1',
    'pgadmin3', 
    'postgresql-contrib',
    'python-psycopg2',

    "binutils",
    "libproj-dev",
    "gdal-bin"
    ])

    if compile_pkgs:
        run("mkdir -p ~/pkgs")
        with cd("~/pkgs"):
             # Download and install the latest GEOS package (http://trac.osgeo.org/geos/).
            # Ubuntu provides a version that is too old for our purposes.
            run("wget http://download.osgeo.org/geos/geos-3.3.8.tar.bz2")
            run("tar xjf geos-3.3.8.tar.bz2")
            with cd("geos-3.3.8"):
                run("./configure")
                run("make")
                sudo("make install")
            # http://docs.djangoproject.com/en/dev/ref/contrib/gis/install/#ibex
            # Download and install some more stuff for proj (from the Django documentation)
            run("wget http://download.osgeo.org/proj/proj-datumgrid-1.5.tar.gz")
            run("wget http://download.osgeo.org/proj/proj-4.8.0.tar.gz")
            run("tar xzf proj-4.8.0.tar.gz")
            with cd("proj-4.8.0/nad"):
                run("tar xzf ../../proj-datumgrid-1.5.tar.gz")
            with cd("proj-4.8.0"):
                run("./configure")
                run("make")
                sudo("make install")
                # Download and install GDAL
            # run("wget http://download.osgeo.org/gdal/gdal-1.9.2.tar.gz")
            # run("tar xzf gdal-1.9.2.tar.gz")
            # with cd("gdal-1.9.2"):
                # run("./configure")
                # run("make") # THIS TAKES LONG
                # sudo("make install")
                # from django.contrib.gis import gdal
                # gdal_check = gdal.HAS_GDAL
            # Download and install the latest PostGIS package
            # run("wget http://download.osgeo.org/postgis/source/postgis-2.1.5.tar.gz")
            # run("tar xzf postgis-2.1.5.tar.gz")
            # with cd("postgis-2.1.5"):
                # run("./configure")
                # run("make")
                # sudo("make install")

    # Make sure PostGIS can find GEOS
    sudo("ldconfig")
    setup_geo_dbs()
    
@task
def setup_geo_dbs():
    run("sudo -u postgres /bin/bash /vagrant/conf/create_template_postgis_debian.sh")

@task
def remove_template_postgis():
    run("sudo -u postgres dropdb template_postgis")        
    
def setup_django():
    pass
