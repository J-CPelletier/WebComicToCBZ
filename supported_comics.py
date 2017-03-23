supported_comics = {
    "xkcd": ("http://xkcd.com/1/", "//a[@rel='next']/@href", "//div[@id='comic']//img/@src"),
    "Nedroid": ("http://nedroid.com/2005/09/2210-whee/", "//div[@class='nav-next']/a/@href", "//div[@id='comic']/img/@src"),
    "JL8": ("http://limbero.org/jl8/1", "//b[2]/a/@href", "//img/@src"),
    "SMBC": ("http://www.smbc-comics.com/comic/2002-09-05", "//a[@class='next']/@href", "//img[@id='cc-comic']/@src"),
    "Blindsprings": ("http://www.blindsprings.com/comic/blindsprings-cover-book-one", "//a[@class='next']/@href", "//img[@id='cc-comic']/@src"),
    "TheAbominableCharlesChristopher": ("http://abominable.cc/post/44164796353/episode-one", "//span[@class='next_post']//@href", "//div[@class='photo']//img/@src"),
    "GuildedAge": ("http://guildedage.net/comic/chapter-1-cover/", "//a[@class='navi comic-nav-next navi-next']/@href", "//div[@id='comic']//img/@src"),
    "TalesOfElysium": ("http://ssp-comics.com/comics/toe/?page=1", "//a[button/@id='nextButton']/@href", "//div[@id='ImageComicContainer']//img/@src"),
    "AmazingSuperPowers": ("http://www.amazingsuperpowers.com/2007/09/heredity/", "//a[@class='navi navi-next']/@href", "//div[@class='comicpane']/img/@src"),
    "Gunshow": ("http://gunshowcomic.com/1", "(//span[@class='snavb'])[4]/a/@href", "//img[@class='strip']/@src")
}
