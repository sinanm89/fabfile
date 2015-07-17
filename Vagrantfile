# Vagrantfile API/syntax version. Don't touch unless you know what you're doing!
VAGRANTFILE_API_VERSION = "2"

Vagrant.configure(VAGRANTFILE_API_VERSION) do |config|
    config.vm.box = "ubuntu1404"
    config.vm.define "fabric_test" do |cfg|
        cfg.vm.network "private_network", ip: "1.2.3.4"
        cfg.vm.network "forwarded_port", guest: 8000, host: 8008
        cfg.vm.network "forwarded_port", guest: 80, host: 8080
        cfg.vm.synced_folder ".", "/vagrant", type:"nfs"
    end
end

