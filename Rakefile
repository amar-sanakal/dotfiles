task    :default   =>  [:install]

desc    "installs the dotfiles"
task    :install do
    Dir.chdir()
    this_directory = File.dirname(__FILE__)
    Dir.entries(this_directory).sort.each do |file|
        if file =~ /^(\....*)$/
            next if file =~ /^\.git(|ignore)$/
            linkname = File.basename(file)
            if File.symlink?(linkname)
                puts "link: #{linkname} already exists -> #{File.readlink(linkname)}"
            elsif File.file?(linkname)
                puts "file: #{linkname} already exists"
                puts "#{linkname}: backup or remove it and run this command again, if you want it replaced"
            else
                puts "creating symbolic link for #{linkname}"
                File.symlink(File.join(this_directory, file), linkname)
            end
        end
    end
end
