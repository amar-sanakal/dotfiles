task    :default   =>  [:install]

desc    "installs the dotfiles"
task    :install do
    Dir.chdir()
    Dir.entries("dotfiles").sort.each do |file|
        if file =~ /^(\....*)$/
            next if file =~ /^\.git(|ignore)$/
            linkname = File.basename(file)
            if File.symlink?(linkname)
                puts "link: #{linkname} already exists -> #{File.readlink(linkname)}"
            elsif File.file?(linkname)
                puts "file: #{linkname} already exists"
                puts "#{linkname}: backup or remove it and run this comand again, if you want it replaced"
            else
                puts "creating symbolic link for #{linkname}"
                File.symlink(File.join("dotfiles", file), linkname)
            end
        end
    end
end
