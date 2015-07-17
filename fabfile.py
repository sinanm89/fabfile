
from fabric.api import *
from fabric.contrib.files import exists
from fabric.utils import puts
from fabtools.vagrant import vagrant
from fabtools import require, fabtools

import hashlib

@task
def setup(vagrant=False):
    """
    I have no strings attached.
    """
    if vagrant:
        puts("--------STARTING IN VAGRANT MODE----------")
    else:
        puts("--------STARTING IN PRODUCTION MODE----------")

    db_name = prompt("Enter your db name:")
    db_user = prompt("Enter your db username:")
    db_password = prompt("Enter your db password:")

    try:
        run('ln -s /vagrant ~/.')
    except:
        puts("linked file already exists")

    sudo("locale-gen en_US.UTF-8")
    sudo("dpkg-reconfigure locales")
    sudo("""sh -c "echo 'LC_ALL=en_US.UTF-8\nLANG=en_US.UTF-8' >> /etc/default/locale" """)
    
    sudo("apt-get update")
    sudo("apt-get upgrade")

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
        
        # geo django setup is installed via a task function below
    ])
    sudo("pip install virtualenv")
    run('virtualenv env')
    with fabtools.python.virtualenv('/home/vagrant/env'):
            run("pip install -r /home/vagrant/vagrant/webserver/requirements.pip")

    sudo("echo 'local all postgres trust' | sudo tee -a /etc/postgresql/9.3/main/pg_hba.conf")
    sudo("echo 'local all all trust' | sudo tee -a /etc/postgresql/9.3/main/pg_hba.conf")
    sudo("service postgresql restart")

    setup_postgresql(db_name=None, db_user=db_user, db_password=db_password)

@task
def setup_postgresql(db_name="databasename", db_user="databasedbu", db_password=None):
    
    if db_password == None:
        db_name = prompt("Enter your db name:")
        db_user = prompt("Enter your db username:")
        db_password = prompt("Enter your db password:")
    password = "md5" + hashlib.md5(db_password+db_user).hexdigest()
    puts("DB hashed password is : {0}".format(password)))
    with settings(warn_only=True):
        sudo("su postgres -c 'createdb -E UTF8 -T template0 --locale=en_US.utf8 template_postgis'")
        # these should be done with geo-libraries theyre not necessary for a skeleton
        # sudo("su postgres -c 'createlang -d template_postgis plpgsql'")
        # sudo("""su postgres -c "echo UPDATE pg_database SET datistemplate=\\'true\\' WHERE datname=\\'template_postgis\\'\\; | psql -d postgres " """)
        # sudo("su postgres -c 'psql -d template_postgis -f /usr/share/postgresql/9.1/contrib/postgis-1.5/postgis.sql' ")
        # sudo("su postgres -c 'psql -d template_postgis -f /usr/share/postgresql/9.1/contrib/postgis-1.5/spatial_ref_sys.sql' ")
        # sudo("""su postgres -c 'psql -d template_postgis -c "GRANT ALL ON geometry_columns TO PUBLIC;"' """) # Enabling users to alter spatial tables

        sudo("""psql -U postgres -c "CREATE ROLE %s WITH ENCRYPTED PASSWORD '%s' NOSUPERUSER CREATEDB NOCREATEROLE INHERIT LOGIN;" """ % (db_user, password))
        sudo("su postgres -c 'createdb -T template_postgis -O %s %s' " % (db_user, db_name))


def setup_geodjango():
    """
    I THINK THESE ARE INSTALLED VIA THE DEP PACKAGES
    """
    
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
    'python-psycopg2',
    
    # geo django setup
    # These are enough for the moment, tested on versus
    'libproj-dev',
    'libgeos-dev',
    'libgdal-dev',
    'python-gdal'
    ])
    
    # run("mkdir -p ~/pkgs")
    # with cd("~/pkgs"):
    #     # http://docs.djangoproject.com/en/dev/ref/contrib/gis/install/#ibex
    #     # Download and install some more stuff for proj (from the Django documentation)
    #     run("wget http://download.osgeo.org/proj/proj-datumgrid-1.4.tar.gz")
    #     run("mkdir -p nad")
    #     with cd("nad"):
    #         run("tar xzf ../proj-datumgrid-1.4.tar.gz")
    #         run("nad2bin null < null.lla")
    #         sudo("cp null /usr/share/proj")
    #     # Download and install the latest GEOS package (http://trac.osgeo.org/geos/).
    #     # Ubuntu provides a version that is too old for our purposes.
    #     run("wget http://download.osgeo.org/geos/geos-3.2.2.tar.bz2")
    #     run("tar xvjf geos-3.2.2.tar.bz2")
    #     with cd("geos-3.2.2"):
    #         run("./configure")
    #         sudo("make && make install")
    #     # Download and install the latest PostGIS package
    #     run("wget http://postgis.refractions.net/download/postgis-1.5.2.tar.gz")
    #     run("tar xvzf postgis-1.5.2.tar.gz")
    #     with cd("postgis-1.5.2"):
    #         run("./configure")
    #         sudo("make && make install")
    #     # Download and install GDAL
    #     run("wget http://download.osgeo.org/gdal/gdal-1.7.3.tar.gz")
    #     run("tar xzf gdal-1.7.3.tar.gz")
    #     with cd("gdal-1.7.3"):
    #         run("./configure")
    #         sudo("make && make install")
    # # Make sure PostGIS can find GEOS
    # sudo("ldconfig")
    # # Set up template_postgis database
    # with cd("/var/lib/postgresql"):
    #     put(script("create_template_postgis-1.5.sh"), ".", mode="0755")
    #     sudo("./create_template_postgis-1.5.sh", user="postgres")

def setup_django():
    pass
