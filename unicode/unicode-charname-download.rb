#!/usr/bin/env ruby

require 'mechanize'

SURFACE = ARGV.delete("-s")

abort "usage : #{$0} (-s:surface)" unless ARGV.empty?

class UnicodeChar < Struct.new(:code, :name)
    def surface
        hex = self.code.hex
        if (hex >= 0x00 and hex <= 0x1F) or hex == 0x7F
            ""
        else
            hex.chr("utf-8") rescue ""
        end
    end

    def to_s(surface=false)
        surface ? to_a.insert(1,self.surface).join("\t") : to_a.join("\t")
    end

end


agent = Mechanize.new
agent.get("https://unicode.org/charts/charindex.html")
#agent.get("file://" + File.expand_path("charindex.html", File.dirname(__FILE__)))


tables = agent.page.search('table[class="subtle-nb"]')

list = []
tables.each{ |tb|
    tb.search('tr').each{ |tr|
        tds = tr.search('td')
        next if tds.empty?

        c = UnicodeChar.new(*tds.map{ |td| td.text }.reverse)

        next unless c.code.match(/^[0-9A-F]+$/)

        list << c
    }
}

# sort by code
list.sort_by!{ |c| c.code.hex }

list.group_by{ |c| c.code }.each{ |code, array|

    if array.length > 1
        upcases = array.select{ |c| c.name == c.name.upcase }
        if upcases.length > 1
            tgt = upcases.min{ |c| c.name.count(",")}
        elsif upcases.length == 1
            tgt = upcases.first
        else
            tgt = array.min{ |c| c.name.count(",")}
        end
    else
        tgt = array.first
    end

    puts SURFACE ? tgt.to_s(true) : tgt
}




