desc    "installs the dotfiles"
task    :install do
    Dir.chdir()
    Dir.new("dotfiles").each do |file|
        if file !~ /^(\.|\.\.)$/
            linkname = File.basename(file)
            if File.symlink?(linkname)
                puts "#{linkname} already exists"
            else
                File.symlink(file, File.basename(file))
            end
        end
    end
end
