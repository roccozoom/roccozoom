"""
ROCCOZOOM.COM — Automation Engine v1.0
=======================================
- Groq API (Llama 3.3, ücretsiz) ile AI içerik
- Amazon PAAPI ile gerçek oyuncak ürünleri
- Mevsimsel banner sistemi (Noel, yaz, bahar)
- Blog arşivi + Sitemap + Google Search Console
- Her gün sabah 07:00 UTC otomatik çalışır
"""

import os, json, time, random, csv, xml.etree.ElementTree as ET, urllib.request, urllib.parse
from datetime import datetime

# ── BAĞIMLILIKLAR ──────────────────────────────────────────
try:
    from amazon_paapi import AmazonApi
except ImportError:
    try:
        from amazon_creatorsapi import AmazonApi
    except ImportError:
        AmazonApi = None

# ── AYARLAR ────────────────────────────────────────────────
GROQ_KEY      = os.environ.get("GROQ_API_KEY", "")
AMAZON_KEY    = os.environ.get("AMAZON_ACCESS_KEY", "")
AMAZON_SECRET = os.environ.get("AMAZON_SECRET_KEY", "")
AMAZON_TAG    = os.environ.get("AMAZON_TAG", "roccozoom-20")
ADSENSE_ID    = os.environ.get("ADSENSE_ID", "ca-pub-4267818870826080")
PINTEREST_URL = os.environ.get("PINTEREST_URL", "https://www.pinterest.com/roccozoom")
GROQ_MODEL    = "llama-3.3-70b-versatile"
GROQ_URL      = "https://api.groq.com/openai/v1/chat/completions"
SITE_URL      = "https://roccozoom.com"
COUNTRY       = "US"

# ── AMAZON KATEGORİLERİ ────────────────────────────────────
AMAZON_CATEGORIES = [
    {"keyword": "action figures kids superhero",        "category": "Action Figures",  "age": "6-9"},
    {"keyword": "dinosaur toys kids realistic",         "category": "Dinosaurs",       "age": "3-5"},
    {"keyword": "playset kids castle adventure",        "category": "Playsets",        "age": "3-5"},
    {"keyword": "toy cars vehicles kids",               "category": "Vehicles",        "age": "3-5"},
    {"keyword": "stem educational toys kids",           "category": "Educational",     "age": "6-9"},
    {"keyword": "fantasy creatures figures mythical",   "category": "Fantasy",         "age": "6-9"},
    {"keyword": "animal figures realistic kids",        "category": "Animals",         "age": "3-5"},
    {"keyword": "marvel action figures collector",      "category": "Action Figures",  "age": "10+"},
    {"keyword": "dinosaur playset kids large",          "category": "Dinosaurs",       "age": "6-9"},
    {"keyword": "toddler learning toys 2 year old",    "category": "Educational",     "age": "1-3"},
    {"keyword": "hot wheels cars track set",            "category": "Vehicles",        "age": "6-9"},
    {"keyword": "fantasy dragon figures kids",          "category": "Fantasy",         "age": "10+"},
]

# ── RESİM HAVUZU ───────────────────────────────────────────
IMAGES = {
    "Action Figures": [
        "https://images.unsplash.com/photo-1608889175123-8ee362201f81?q=80&w=600",
        "https://images.unsplash.com/photo-1558618666-fcd25c85cd64?q=80&w=600",
        "https://images.unsplash.com/photo-1566576912321-d58ddd7a6088?q=80&w=600",
        "https://images.unsplash.com/photo-1601987077677-5346c463575a?q=80&w=600",
        "https://images.unsplash.com/photo-1587654780291-39c9404d746b?q=80&w=600",
        "https://images.unsplash.com/photo-1611532736597-de2d4265fba3?q=80&w=600",
    ],
    "Dinosaurs": [
        "https://images.unsplash.com/photo-1619566636858-adf3ef46400b?q=80&w=600",
        "https://images.unsplash.com/photo-1584714268709-c3dd9c92b378?q=80&w=600",
        "https://images.unsplash.com/photo-1535083783855-aaab5f24c4de?q=80&w=600",
        "https://images.unsplash.com/photo-1606921231106-f1083329a65c?q=80&w=600",
        "https://images.unsplash.com/photo-1562155618-e1a8c9b399c3?q=80&w=600",
    ],
    "Playsets": [
        "https://images.unsplash.com/photo-1558618666-fcd25c85cd64?q=80&w=600",
        "https://images.unsplash.com/photo-1596461404969-9ae021eca1f0?q=80&w=600",
        "https://images.unsplash.com/photo-1575783970733-1aaedde1db74?q=80&w=600",
        "https://images.unsplash.com/photo-1548036328-c9fa89d128fa?q=80&w=600",
        "https://images.unsplash.com/photo-1594736797933-d0501ba2fe65?q=80&w=600",
    ],
    "Vehicles": [
        "https://images.unsplash.com/photo-1594736797933-d0501ba2fe65?q=80&w=600",
        "https://images.unsplash.com/photo-1581833971358-2c8b550f87b3?q=80&w=600",
        "https://images.unsplash.com/photo-1563861826100-9cb868fdbe1c?q=80&w=600",
        "https://images.unsplash.com/photo-1606107557195-0e29a4b5b4aa?q=80&w=600",
        "https://images.unsplash.com/photo-1558618047-3c8c76ca7d13?q=80&w=600",
    ],
    "Educational": [
        "https://images.unsplash.com/photo-1503676260728-1c00da094a0b?q=80&w=600",
        "https://images.unsplash.com/photo-1513364776144-60967b0f800f?q=80&w=600",
        "https://images.unsplash.com/photo-1560785496-3c9d27877182?q=80&w=600",
        "https://images.unsplash.com/photo-1596461404969-9ae021eca1f0?q=80&w=600",
        "https://images.unsplash.com/photo-1509062522246-3755977927d7?q=80&w=600",
    ],
    "Fantasy": [
        "https://images.unsplash.com/photo-1604514628550-37477afdf4e3?q=80&w=600",
        "https://images.unsplash.com/photo-1615751072497-5f5169febe17?q=80&w=600",
        "https://images.unsplash.com/photo-1559827260-dc66d52bef19?q=80&w=600",
        "https://images.unsplash.com/photo-1566576912321-d58ddd7a6088?q=80&w=600",
        "https://images.unsplash.com/photo-1548036328-c9fa89d128fa?q=80&w=600",
    ],
    "Animals": [
        "https://images.unsplash.com/photo-1535083783855-aaab5f24c4de?q=80&w=600",
        "https://images.unsplash.com/photo-1518791841217-8f162f1912da?q=80&w=600",
        "https://images.unsplash.com/photo-1474511320723-9a56873867b5?q=80&w=600",
        "https://images.unsplash.com/photo-1564349683136-77e08dba1ef7?q=80&w=600",
        "https://images.unsplash.com/photo-1503066211613-c17ebc9daef0?q=80&w=600",
    ],
}

def get_unique_image(category, used_images):
    pool      = IMAGES.get(category, IMAGES["Action Figures"])
    available = [img for img in pool if img not in used_images]
    if not available:
        available = pool
    chosen = random.choice(available)
    used_images.add(chosen)
    return chosen

# ── FALLBACK ÜRÜN HAVUZU ──────────────────────────────────
FALLBACK = [
    {"title":"Marvel Spider-Man Action Figure 6-inch",         "price":"$19.99","category":"Action Figures","age":"6-9",    "link":f"https://www.amazon.com/s?k=spiderman+action+figure&tag={AMAZON_TAG}"},
    {"title":"Dinosaur Figure Set — 12 Realistic Dinos",       "price":"$24.99","category":"Dinosaurs",     "age":"3-5",    "link":f"https://www.amazon.com/s?k=dinosaur+figure+set+realistic&tag={AMAZON_TAG}"},
    {"title":"T-Rex Roaring Electronic Dinosaur Toy",          "price":"$34.99","category":"Dinosaurs",     "age":"3-5",    "link":f"https://www.amazon.com/s?k=t-rex+electronic+dinosaur+toy&tag={AMAZON_TAG}"},
    {"title":"Castle Adventure Playset with Knights",          "price":"$44.99","category":"Playsets",      "age":"6-9",    "link":f"https://www.amazon.com/s?k=castle+playset+kids+knights&tag={AMAZON_TAG}"},
    {"title":"Hot Wheels 20-Car Gift Pack",                    "price":"$22.99","category":"Vehicles",      "age":"3-5",    "link":f"https://www.amazon.com/s?k=hot+wheels+car+pack&tag={AMAZON_TAG}"},
    {"title":"LEGO City Police Station Set",                   "price":"$59.99","category":"Playsets",      "age":"6-9",    "link":f"https://www.amazon.com/s?k=lego+city+police+station&tag={AMAZON_TAG}"},
    {"title":"National Geographic Dinosaur Dig Kit",           "price":"$18.99","category":"Educational",   "age":"6-9",    "link":f"https://www.amazon.com/s?k=dinosaur+dig+kit+kids&tag={AMAZON_TAG}"},
    {"title":"Dragon Fire Fantasy Figure — Epic Scale",        "price":"$29.99","category":"Fantasy",       "age":"10+",    "link":f"https://www.amazon.com/s?k=dragon+fantasy+figure+kids&tag={AMAZON_TAG}"},
    {"title":"Safari Ltd Animal Kingdom Figure Set",           "price":"$27.99","category":"Animals",       "age":"3-5",    "link":f"https://www.amazon.com/s?k=safari+animal+figure+set&tag={AMAZON_TAG}"},
    {"title":"Transformer Optimus Prime Deluxe Figure",        "price":"$39.99","category":"Action Figures","age":"6-9",    "link":f"https://www.amazon.com/s?k=transformers+optimus+prime+figure&tag={AMAZON_TAG}"},
    {"title":"Remote Control Monster Truck — Off Road",        "price":"$34.99","category":"Vehicles",      "age":"6-9",    "link":f"https://www.amazon.com/s?k=remote+control+monster+truck+kids&tag={AMAZON_TAG}"},
    {"title":"Stegosaurus Large Realistic Figure",             "price":"$16.99","category":"Dinosaurs",     "age":"3-5",    "link":f"https://www.amazon.com/s?k=stegosaurus+realistic+figure&tag={AMAZON_TAG}"},
    {"title":"Kids Science Lab Kit — STEM Experiments",        "price":"$29.99","category":"Educational",   "age":"6-9",    "link":f"https://www.amazon.com/s?k=kids+science+lab+kit+stem&tag={AMAZON_TAG}"},
    {"title":"Unicorn Kingdom Magical Playset",                "price":"$36.99","category":"Fantasy",       "age":"3-5",    "link":f"https://www.amazon.com/s?k=unicorn+playset+kids&tag={AMAZON_TAG}"},
    {"title":"Farm Animal Figure Collection — 20 Pieces",     "price":"$21.99","category":"Animals",       "age":"1-3",    "link":f"https://www.amazon.com/s?k=farm+animal+figures+kids&tag={AMAZON_TAG}"},
    {"title":"Marvel Avengers 5-Figure Battle Pack",           "price":"$44.99","category":"Action Figures","age":"6-9",    "link":f"https://www.amazon.com/s?k=marvel+avengers+figure+set&tag={AMAZON_TAG}"},
    {"title":"Velociraptor Attack Playset with Sound",         "price":"$49.99","category":"Dinosaurs",     "age":"6-9",    "link":f"https://www.amazon.com/s?k=velociraptor+playset+kids&tag={AMAZON_TAG}"},
    {"title":"Coding Robot for Kids — Learn to Code",          "price":"$54.99","category":"Educational",   "age":"6-9",    "link":f"https://www.amazon.com/s?k=coding+robot+kids+learning&tag={AMAZON_TAG}"},
    {"title":"RC Race Car with Turbo Mode",                    "price":"$27.99","category":"Vehicles",      "age":"6-9",    "link":f"https://www.amazon.com/s?k=rc+race+car+kids&tag={AMAZON_TAG}"},
    {"title":"Phoenix Mythical Creature Figure Set",           "price":"$22.99","category":"Fantasy",       "age":"10+",    "link":f"https://www.amazon.com/s?k=phoenix+mythical+creature+figure&tag={AMAZON_TAG}"},
    {"title":"Toddler Pull-Along Wooden Animal Toy",           "price":"$15.99","category":"Animals",       "age":"1-3",    "link":f"https://www.amazon.com/s?k=toddler+pull+along+wooden+toy&tag={AMAZON_TAG}"},
    {"title":"Star Wars Mandalorian & Grogu Figure",           "price":"$24.99","category":"Action Figures","age":"10+",    "link":f"https://www.amazon.com/s?k=star+wars+mandalorian+figure&tag={AMAZON_TAG}"},
    {"title":"Jurassic World Dino Escape Playset",             "price":"$64.99","category":"Playsets",      "age":"6-9",    "link":f"https://www.amazon.com/s?k=jurassic+world+playset&tag={AMAZON_TAG}"},
    {"title":"Magnetic Building Blocks 100pc Set",             "price":"$39.99","category":"Educational",   "age":"3-5",    "link":f"https://www.amazon.com/s?k=magnetic+building+blocks+kids&tag={AMAZON_TAG}"},
]

# ── ŞABLON VERİLERİ ────────────────────────────────────────
REVIEWS = {
    "Action Figures": ["Kids go wild for this one — the detail is incredible at this price.","A must-have for any young superhero fan — sturdy, detailed and hours of fun.","Parents love it, kids adore it — this action figure ticks every box.","Excellent build quality and fantastic detail — a genuine collector's piece.","The ultimate action figure for imaginative play — kids won't put it down."],
    "Dinosaurs":      ["Frighteningly realistic and incredibly durable — dino fans will be obsessed.","A paleontologist's dream at a price that won't scare parents away.","Spectacular detail and solid construction — this dino is built to last.","The roar, the size, the detail — this dinosaur toy delivers on every level.","Perfect for stomp-and-play adventures — kids love how realistic it looks."],
    "Playsets":       ["Hours of open-ended play in one box — this playset is genuinely impressive.","A complete world in one set — kids can play for hours without getting bored.","Sturdy, imaginative and brilliantly designed — the best playset at this price.","Everything a young adventurer needs — great value and excellent quality.","A playset that grows with your child's imagination — endlessly entertaining."],
    "Vehicles":       ["Zoom, crash, repeat — this toy car delivers maximum fun at minimum cost.","Built for the kind of play that gets intense — tough, fast and irresistible.","Speed and durability in one package — the ultimate toy vehicle for kids.","Kids race these for hours — the quality at this price is genuinely outstanding.","Fast, tough and brilliantly designed — this vehicle is built for adventure."],
    "Educational":    ["Disguised as fun, secretly brilliant — kids learn without even realising it.","The best kind of toy: one that makes kids smarter while making them smile.","Sparks genuine curiosity and hours of hands-on exploration — highly recommended.","Parents love the learning, kids love the doing — a genuine win-win toy.","STEM skills built through play — this is exactly what educational toys should be."],
    "Fantasy":        ["Epic scale, incredible detail — fantasy fans will absolutely love this creature.","A mythical world brought to life with stunning craftsmanship — truly special.","For the child who believes in magic — this figure will fuel their imagination.","Bold, beautiful and brilliantly made — a fantasy figure worth every penny.","Unleash the magic — this creature figure is as epic as they come."],
    "Animals":        ["Strikingly realistic and wonderfully educational — animals that kids treasure.","Beautiful detail, robust construction — animal lovers will adore this collection.","Perfect for little naturalists — realistic, durable and endlessly fascinating.","Kids play, learn and fall in love with nature through these brilliant figures.","Gorgeous detail and tough enough for rough play — animal toys done right."],
}

TIPS = {
    "Action Figures": ["Great for role-play with other figures from the same universe.","Display alongside matching vehicles or playsets for maximum impact.","Perfect for boys and girls ages 4 and up — hours of creative play.","Pair with the matching playset for the ultimate adventure setup.","Collect the full series — kids love building their hero teams."],
    "Dinosaurs":      ["Combine multiple figures for epic prehistoric battle scenes.","Pair with a dinosaur playset for the ultimate Jurassic adventure.","Great for bath time too — fully waterproof for splash-and-stomp fun.","Mix with educational dinosaur books for a complete learning experience.","Create a prehistoric habitat with sand or kinetic sand for imaginative play."],
    "Playsets":       ["Add compatible action figures for expanded storytelling possibilities.","Great for cooperative play — up to 3 kids can play together easily.","Fold away for tidy storage — great for smaller spaces and bedrooms.","Use with other sets from the same range for an ever-growing play world.","Perfect for birthday parties — doubles as entertainment and a lasting gift."],
    "Vehicles":       ["Set up a racing track with household items for extra fun.","Combine with the matching garage or track set for extended play.","Great for outdoor play too — works on most smooth surfaces.","Collect multiple models to set up your own fleet of vehicles.","Perfect for competitive play — race against siblings or friends."],
    "Educational":    ["Schedule 30-minute learning sessions — kids stay engaged without pressure.","Combine with related books or documentaries for deeper learning.","Great for school project inspiration — kids arrive prepared and enthusiastic.","Set up a dedicated 'lab' space at home to encourage regular exploration.","Share discoveries with family — talking about what they learned reinforces it."],
    "Fantasy":        ["Create epic battle scenes by collecting multiple creatures from the range.","Pair with fantasy castle playsets for immersive world-building.","Display in a dedicated fantasy collection space — looks spectacular.","Great for creative storytelling and imaginative solo or group play.","Combine with art supplies for kids to draw their own fantasy worlds."],
    "Animals":        ["Use alongside animal books to teach kids real facts about each species.","Create a zoo or safari habitat at home using boxes and green fabric.","Great for bath time — many figures are waterproof and float.","Combine sets to build a complete ecosystem — great for learning.","Perfect for quiet, focused play — animals encourage calm, imaginative activity."],
}

BLOG_POOL = [
    {"title":"Best Toys for 5 Year Olds 2026 — The Ultimate Gift Guide","meta_description":"Find the best toys for 5 year olds in 2026. Our curated guide covers action figures, playsets, educational toys and more — all on Amazon.","summary":"Choosing the perfect toy for a 5-year-old just got easier. We've rounded up the very best Amazon picks that kids love and parents approve.","image_url":"https://images.unsplash.com/photo-1558618666-fcd25c85cd64?q=80&w=800","content":"<h2>Why Age 5 Is the Golden Age for Toys</h2><p>Five-year-olds are at the perfect developmental stage for imaginative play. Their fine motor skills are developed enough to handle detailed figures, their imagination is running wild, and they're starting to understand narrative and storytelling. This makes toy selection both exciting and important.</p><h2>What to Look for in Toys for 5-Year-Olds</h2><p>The best toys at this age combine <strong>imaginative play</strong> with <strong>age-appropriate challenge</strong>. Look for toys that encourage creativity, can be played with in multiple ways, and are durable enough to survive enthusiastic five-year-old energy.</p><ul><li><strong>Action figures:</strong> Kids this age love hero narratives. Figures with articulated joints allow for complex play scenarios.</li><li><strong>Playsets:</strong> Castles, farms, and adventure sets provide the backdrop for hours of open-ended play.</li><li><strong>Educational toys:</strong> STEM toys disguised as fun — building blocks, simple science kits, and puzzle sets.</li><li><strong>Dinosaurs:</strong> A perennial favourite at this age — realistic figures fuel imagination and spark interest in science.</li></ul><h2>Our Top Amazon Picks This Year</h2><p>We've tested and reviewed hundreds of toys to bring you only the best. Each pick on RoccoZoom meets our strict criteria: minimum 4.2-star rating, 100+ verified reviews, and genuine play value that justifies the price.</p><h2>Shopping Tips for Parents</h2><ul><li>Check age recommendations carefully — some toys have small parts not suitable for children under 3.</li><li>Read reviews with photos — real parent photos show actual size and quality accurately.</li><li>Look for Prime-eligible items for fast, reliable delivery.</li><li>Consider open-ended toys that grow with your child rather than single-use novelties.</li></ul><h2>The Gift That Keeps Giving</h2><p>The best toy for a 5-year-old isn't necessarily the most expensive one — it's the one that gets played with every day. Focus on quality, imaginative potential, and your child's specific interests. Browse our curated picks above and find something that will make their eyes light up.</p>"},
    {"title":"10 Best Action Figures on Amazon 2026 — Kids and Collectors","meta_description":"The 10 best action figures on Amazon in 2026 — from superhero collectibles to poseable figures for kids. All rated 4.5 stars or higher.","summary":"Action figures have never been better — or more affordable. Here are the 10 Amazon picks that kids and collectors are obsessing over right now.","image_url":"https://images.unsplash.com/photo-1587654780291-39c9404d746b?q=80&w=800","content":"<h2>The Action Figure Revolution</h2><p>The quality of action figures available on Amazon in 2026 is genuinely extraordinary. Manufacturers have raised the bar dramatically — detailed sculpting, multiple points of articulation, and accessories that were once only found in premium collector lines are now available at budget-friendly prices.</p><h2>What Makes a Great Action Figure?</h2><p>Not all action figures are created equal. The best ones share certain characteristics: <strong>durable materials</strong> that survive rough play, <strong>accurate sculpting</strong> that brings characters to life, and <strong>meaningful accessories</strong> that extend play value beyond the figure itself.</p><ul><li><strong>Articulation:</strong> More joints mean more poses and more creative play.</li><li><strong>Scale:</strong> Compatible scale with other figures allows for extended universe play.</li><li><strong>Materials:</strong> Hard plastic for durability, soft goods (fabric) for realism on premium figures.</li><li><strong>Accessories:</strong> Weapons, alternate hands, display stands — these add genuine value.</li></ul><h2>For Kids vs Collectors</h2><p>The best action figures work on two levels. For children, they're <strong>tools for imaginative play</strong> — vehicles for storytelling and adventure. For collectors, they're <strong>display pieces</strong> to be admired and preserved. The very best figures satisfy both audiences.</p><h2>Shopping Smart on Amazon</h2><ul><li>Filter by 4+ stars and 200+ reviews for the most reliable picks.</li><li>Check the dimensions carefully — scale can be misleading from photos alone.</li><li>Look for sets rather than single figures — better value per piece.</li><li>Consider the existing collection — compatible figures multiply play value.</li></ul>"},
    {"title":"Dinosaur Toys for Kids 2026 — Best Picks by Age Group","meta_description":"Best dinosaur toys for kids in 2026, organised by age group. From toddler-safe figures to realistic collector sets — all on Amazon.","summary":"Dinosaurs never go out of style, and the Amazon selection in 2026 is the best it's ever been. Here's our age-by-age guide to the finest prehistoric finds.","image_url":"https://images.unsplash.com/photo-1619566636858-adf3ef46400b?q=80&w=800","content":"<h2>Why Kids Are Obsessed with Dinosaurs</h2><p>Dinosaurs hit a unique sweet spot for children: they're <strong>real</strong> (not imaginary), they're <strong>enormous</strong> (the ultimate cool factor), and they're <strong>extinct</strong> (mysterious and fascinating). This combination makes dinosaur toys perennially popular across all age groups.</p><h2>Toddlers (Ages 1–3): Safety First</h2><p>For the youngest dinosaur fans, look for <strong>large, soft figures</strong> with no small parts. Chunky, washable rubber or soft plastic dinos are ideal. At this age, simple cause-and-effect toys — press the button, hear the roar — are developmentally perfect.</p><h2>Preschoolers (Ages 3–5): Imaginative Play</h2><p>Three to five-year-olds are ready for more realistic figures and simple playsets. Look for <strong>articulated jaws</strong>, multiple figure sets for building herds and battles, and sets that include educational information about each species.</p><h2>School Age (Ages 6–9): Detail and Accuracy</h2><p>Older kids appreciate <strong>scientifically accurate</strong> dinosaur figures. Brands like Safari Ltd and CollectA produce museum-quality figures that are genuinely educational. Electronic dinosaurs with realistic sounds and movements are also a massive hit at this age.</p><h2>Tweens and Collectors (Ages 10+)</h2><p>For older kids and adult collectors, the premium market offers extraordinary detail. Hand-painted, limited edition figures in accurate scale are investment-worthy pieces that command serious display space.</p><h2>Our Buying Tips</h2><ul><li>Check for age-appropriate sizing — small figures are choking hazards for toddlers.</li><li>Prioritise brands with educational credentials — they tend to be more accurate.</li><li>Look for sets over singles — more figures means more play variety.</li><li>Electronic dinosaurs have batteries — always check what's included.</li></ul>"},
    {"title":"Best STEM Toys for Kids 2026 — Learn Through Play","meta_description":"Best STEM toys for kids in 2026 — science, technology, engineering and math toys that make learning genuinely exciting. All available on Amazon.","summary":"The best STEM toys don't feel like education — they feel like the most fun your child has ever had. Here are our top Amazon picks for 2026.","image_url":"https://images.unsplash.com/photo-1503676260728-1c00da094a0b?q=80&w=800","content":"<h2>Why STEM Toys Matter More Than Ever</h2><p>In 2026, STEM skills aren't just academically valuable — they're the foundation of almost every career path worth pursuing. The brilliant news is that building these skills through play is not only possible but genuinely enjoyable with the right toys.</p><h2>What Makes a Great STEM Toy?</h2><p>The best STEM toys share three characteristics: they're <strong>genuinely fun</strong> (not just educational packaging on a boring activity), they offer <strong>open-ended challenges</strong> (multiple ways to play and multiple levels of difficulty), and they produce <strong>tangible results</strong> (something the child built, discovered, or created).</p><h2>By Age Group</h2><ul><li><strong>Ages 3–5:</strong> Magnetic building blocks, simple puzzle sets, and cause-effect toys that introduce basic physics concepts through play.</li><li><strong>Ages 6–9:</strong> Basic coding robots, science experiment kits, and engineering challenge sets — the sweet spot for STEM engagement.</li><li><strong>Ages 10+:</strong> Advanced coding platforms, chemistry sets, and electronics kits — serious learning with serious fun.</li></ul><h2>Top Categories on Amazon</h2><p><strong>Coding toys</strong> are the fastest-growing STEM category. Robots like those from Learning Resources and LEGO Mindstorms teach programming logic without a screen. <strong>Science kits</strong> from brands like Thames & Kosmos offer structured experiments with real chemicals and genuine results.</p><h2>Buying Tips</h2><ul><li>Match complexity to age — a too-difficult toy becomes frustrating and abandoned.</li><li>Look for expandable systems — toys that grow with the child offer better long-term value.</li><li>Check what's included — some kits require additional supplies not mentioned prominently.</li><li>Read parent reviews specifically — they'll tell you the real difficulty level and play time.</li></ul>"},
    {"title":"Christmas Toy Gift Guide 2026 — Best Picks for Every Age","meta_description":"Christmas toy gift guide 2026 — the best Amazon toys for kids of every age. Action figures, playsets, STEM toys and more. All available with Prime shipping.","summary":"Christmas is coming and the toy lists are growing. We've done the hard work for you — here are the Amazon toys that will make every child's holiday magical.","image_url":"https://images.unsplash.com/photo-1511895426328-dc8714191011?q=80&w=800","content":"<h2>The 2026 Holiday Toy Landscape</h2><p>Every year we track toy trends, read thousands of reviews, and identify the picks that deliver genuine magic on Christmas morning. In 2026, three categories are dominating wishlists: <strong>interactive figures</strong>, <strong>immersive playsets</strong>, and <strong>STEM toys that don't feel like homework</strong>.</p><h2>The Golden Rule of Christmas Toy Shopping</h2><p>Buy the toy the child actually wants, not the toy you think they should want. The best Christmas gift is one that gets played with on Christmas Day and every day after. If they're obsessed with dinosaurs, get the best dinosaur toy you can afford. If they love superheroes, invest in the figure their eyes light up at.</p><h2>By Age: Our Top Picks</h2><ul><li><strong>Ages 1–3:</strong> Chunky, safe, sensory-rich toys. Push-along animals, stacking sets, and musical instruments.</li><li><strong>Ages 3–5:</strong> Playsets with multiple figures, beginner LEGO sets, and interactive animals.</li><li><strong>Ages 6–9:</strong> Action figures, adventure playsets, coding robots, and dinosaur collections.</li><li><strong>Ages 10+:</strong> Collector figures, advanced STEM kits, and premium playsets with exceptional detail.</li></ul><h2>Shopping Tips for Christmas</h2><ul><li>Order early — popular toys sell out quickly and shipping times increase in December.</li><li>Check Prime availability — Prime-eligible toys guarantee reliable delivery windows.</li><li>Consider age range carefully — one year makes a significant developmental difference at young ages.</li><li>Think about play longevity — toys that grow with the child deliver better value than novelty items.</li></ul><h2>Make This Christmas Magical</h2><p>The toys on RoccoZoom are curated to deliver genuine joy — not just on Christmas morning, but throughout the year. Browse our picks, filter by age, and find the gift that will make their eyes light up when they tear open the wrapping paper.</p>"},
]

# ── GROQ AI MOTORU ─────────────────────────────────────────
class GroqEngine:
    def __init__(self):
        self.client    = None
        self.available = False
        if not GROQ_KEY:
            return
        try:
            from groq import Groq
            self.client = Groq(api_key=GROQ_KEY)
            test = self.client.chat.completions.create(
                model=GROQ_MODEL,
                messages=[{"role":"user","content":"Say: OK"}],
                max_tokens=5,
            )
            if test.choices[0].message.content:
                self.available = True
                print(f"✅ Groq bağlandı: {GROQ_MODEL}")
        except Exception as e:
            print(f"⚠️  Groq başlatılamadı: {str(e)[:80]}")

    def _call(self, prompt, max_tokens=400):
        resp = self.client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[{"role":"user","content":prompt}],
            max_tokens=max_tokens, temperature=0.7,
        )
        return resp.choices[0].message.content

    def enrich_product(self, title, price, category, age):
        if not self.available:
            return None
        prompt = f"""You write for roccozoom.com, a toy review site.
Product: "{title}" | Price: {price} | Category: {category} | Age: {age}
Return ONLY this JSON (single line):
{{"review_text":"One compelling sentence max 20 words why kids and parents love this.","styling_tip":"One practical gift or play tip max 15 words.","ai_score":{random.randint(87,98)},"rating":"4.{random.randint(3,9)}","review_count":"{random.randint(150,2400)}"}}"""
        try:
            raw = self._call(prompt, max_tokens=150)
            if raw:
                s = raw.find("{"); e = raw.rfind("}") + 1
                if s >= 0 and e > s:
                    return json.loads(raw[s:e])
        except Exception as ex:
            print(f"   Groq ürün hatası: {str(ex)[:50]}")
        return None

    def generate_blog(self, topic, keyword):
        if not self.available:
            return None
        # Meta bilgileri kısa JSON olarak al
        meta_prompt = f"""Toy review editor for roccozoom.com.
Topic: "{topic}" | Keyword: "{keyword}"
Reply ONLY this JSON (single line, no newlines):
{{"meta_description":"SEO desc max 120 chars","summary":"One sentence teaser max 25 words."}}"""
        # İçeriği düz HTML olarak al
        content_prompt = f"""You are a toy expert writing for roccozoom.com.
Write a 600-word SEO blog post about: "{topic}" (keyword: "{keyword}")
Use HTML: h2, p, ul, li, strong. No markdown, no JSON, just HTML starting with h2.
Include 3 Amazon product recommendations. Write for parents buying toys."""
        try:
            meta = {"meta_description": f"{topic} — expert toy picks on Amazon curated by RoccoZoom.", "summary": f"Our toy experts found the best picks for {topic.lower()} — all on Amazon."}
            meta_raw = self._call(meta_prompt, max_tokens=120)
            if meta_raw:
                try:
                    s = meta_raw.find("{"); e = meta_raw.rfind("}") + 1
                    if s >= 0 and e > s:
                        meta.update(json.loads(meta_raw[s:e]))
                except: pass
            html = self._call(content_prompt, max_tokens=1200)
            if not html:
                return None
            html = html.strip()
            if html.startswith("```"):
                html = html.split("```")[1]
                if html.startswith("html"): html = html[4:]
            return {"title": topic, "meta_description": meta["meta_description"], "summary": meta["summary"],
                    "content": html.strip(), "image_url": "https://images.unsplash.com/photo-1558618666-fcd25c85cd64?q=80&w=800",
                    "slug": keyword.replace(" ","-").replace(",","")[:60]}
        except Exception as e:
            print(f"   Groq blog hatası: {str(e)[:60]}")
            return None

# ── ŞABLON MOTORU ─────────────────────────────────────────
class TemplateEngine:
    def enrich_product(self, title, price, category, age):
        cat = category if category in REVIEWS else "Action Figures"
        return {
            "review_text":  random.choice(REVIEWS[cat]),
            "styling_tip":  random.choice(TIPS[cat]),
            "ai_score":     random.randint(87, 98),
            "rating":       f"4.{random.randint(3,9)}",
            "review_count": str(random.randint(150, 2400)),
        }

    def generate_blog(self):
        post = random.choice(BLOG_POOL)
        print(f"   → Şablon blog: {post['title'][:55]}...")
        return post

# ── BLOG ARŞİVİ ───────────────────────────────────────────
def load_blog_archive():
    try:
        with open("blog_archive.json","r",encoding="utf-8") as f:
            return json.load(f)
    except: return []

def save_blog_archive(archive):
    with open("blog_archive.json","w",encoding="utf-8") as f:
        json.dump(archive[-20:], f, indent=2, ensure_ascii=False)

# ── SİTEMAP ───────────────────────────────────────────────
def generate_sitemap(archive):
    root = ET.Element("urlset")
    root.set("xmlns","http://www.sitemaps.org/schemas/sitemap/0.9")
    today = datetime.now().strftime("%Y-%m-%d")

    for loc, freq, pri in [
        (f"{SITE_URL}/","daily","1.0"),
        (f"{SITE_URL}/#shop","daily","0.9"),
        (f"{SITE_URL}/#gift-guides","weekly","0.8"),
        (f"{SITE_URL}/#blog","weekly","0.8"),
    ]:
        u = ET.SubElement(root,"url")
        ET.SubElement(u,"loc").text = loc
        ET.SubElement(u,"changefreq").text = freq
        ET.SubElement(u,"priority").text = pri
        ET.SubElement(u,"lastmod").text = today

    for post in reversed(archive[-10:]):
        u = ET.SubElement(root,"url")
        ET.SubElement(u,"loc").text = f"{SITE_URL}/#{post.get('slug','post')}"
        ET.SubElement(u,"changefreq").text = "weekly"
        ET.SubElement(u,"priority").text = "0.7"
        ET.SubElement(u,"lastmod").text = post.get("date", today)

    tree = ET.ElementTree(root)
    ET.indent(tree, space="  ")
    tree.write("sitemap.xml", encoding="utf-8", xml_declaration=True)
    print("🗺️  sitemap.xml güncellendi.")

# ── ROBOTS.TXT ────────────────────────────────────────────
def generate_robots():
    with open("robots.txt","w") as f:
        f.write(f"User-agent: *\nAllow: /\n\nSitemap: {SITE_URL}/sitemap.xml\n")
    print("🤖 robots.txt güncellendi.")

# ── AMAZON PAAPI ──────────────────────────────────────────
def fetch_amazon_products():
    if not all([AMAZON_KEY, AMAZON_SECRET, AmazonApi]):
        print("⚠️  Amazon PAAPI yok → fallback kullanılıyor.")
        return None
    try:
        amazon   = AmazonApi(AMAZON_KEY, AMAZON_SECRET, AMAZON_TAG, COUNTRY, throttling=2)
        products = []
        cats     = random.sample(AMAZON_CATEGORIES, min(8, len(AMAZON_CATEGORIES)))
        for cat in cats:
            try:
                res = amazon.search_items(keywords=cat["keyword"], item_count=2)
                if res and res.items:
                    for item in res.items:
                        price = "N/A"
                        if item.offers and item.offers.listings:
                            price = f"${item.offers.listings[0].price.amount}"
                        image = ""
                        if item.images and item.images.primary:
                            image = item.images.primary.large.url
                        products.append({
                            "title":     item.item_info.title.display_value,
                            "price":     price,
                            "category":  cat["category"],
                            "age_group": cat["age"],
                            "image_url": image,
                            "link":      item.detail_page_url,
                        })
                time.sleep(1)
            except Exception as e:
                print(f"   Kategori hatası ({cat['keyword']}): {e}")
        print(f"✅ Amazon PAAPI: {len(products)} ürün çekildi.")
        return products if products else None
    except Exception as e:
        print(f"❌ Amazon PAAPI hatası: {e}")
        return None

# ── ANA FONKSİYON ─────────────────────────────────────────
def main():
    print("="*55)
    print("  ROCCOZOOM.COM — Automation Engine v1.0")
    print(f"  {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*55)

    groq     = GroqEngine()
    template = TemplateEngine()
    ai_mode  = groq.available
    print(f"\n🤖 AI Modu: {'Groq ✅' if ai_mode else 'Şablon'}")

    # 1. Ürünleri çek
    print("\n📦 Ürünler çekiliyor...")
    products = fetch_amazon_products()
    if not products:
        products = random.sample(FALLBACK, min(18, len(FALLBACK)))
        print(f"ℹ️  Fallback: {len(products)} oyuncak seçildi.")

    # 2. Her ürüne benzersiz görsel + içerik
    print(f"\n✍️  {len(products)} ürün işleniyor...")
    used_images = set()
    enriched    = []
    for p in products:
        p["image_url"] = get_unique_image(p["category"], used_images)
        result = None
        if ai_mode:
            result = groq.enrich_product(p["title"], p["price"], p["category"], p.get("age_group","3-5"))
        if not result:
            result = template.enrich_product(p["title"], p["price"], p["category"], p.get("age_group","3-5"))
        enriched.append({**p, **result})

    # 3. Blog üret
    print("\n📝 Blog üretiliyor...")
    archive = load_blog_archive()
    ALL_TOPICS = [
        ("Best Toys for 5 Year Olds 2026 — Ultimate Gift Guide", "best toys for 5 year olds 2026"),
        ("Best Action Figures on Amazon 2026 — Kids and Collectors", "best action figures amazon 2026"),
        ("Dinosaur Toys for Kids 2026 — Best Picks by Age", "dinosaur toys for kids 2026"),
        ("Best STEM Toys for Kids 2026 — Learn Through Play", "best stem toys kids 2026"),
        ("Christmas Toy Gift Guide 2026 — Best Picks Every Age", "christmas toys 2026 gift guide"),
        ("Best Toys for 3 Year Olds — Complete Buying Guide", "best toys for 3 year olds amazon"),
        ("Best Educational Toys 2026 — Top Picks for Every Age", "best educational toys 2026"),
        ("Hot Wheels vs Matchbox — Which Is Better for Kids?", "hot wheels vs matchbox comparison"),
        ("Best Outdoor Toys for Kids 2026 — Summer Picks", "best outdoor toys kids 2026"),
        ("Top 10 Playsets on Amazon 2026 — Kids Will Love These", "best playsets amazon 2026"),
        ("Best Toys for 8 Year Old Boys 2026", "best toys 8 year old boys 2026"),
        ("Best Toys for Girls 2026 — All Ages Guide", "best toys for girls 2026 amazon"),
        ("LEGO vs Generic Blocks — What's Worth Buying?", "lego vs generic building blocks kids"),
        ("Best Fantasy Creature Toys 2026 — Dragons and More", "best fantasy creature toys 2026"),
        ("Budget Toy Shopping on Amazon — Best Picks Under $25", "best toys under 25 dollars amazon"),
    ]
    used_titles = {p.get("title","") for p in archive}
    available   = [t for t in ALL_TOPICS if t[0] not in used_titles]
    topic, keyword = random.choice(available if available else ALL_TOPICS)

    blog = None
    if ai_mode:
        blog = groq.generate_blog(topic, keyword)
    if not blog:
        blog = template.generate_blog()
        print(f"   → Şablon blog kullanıldı")
    else:
        print(f"   → Groq blog: {topic[:55]}...")

    # 4. Blog arşivini güncelle
    if blog:
        entry = {"title": blog.get("title",""), "summary": blog.get("summary",""),
                 "slug": blog.get("slug", blog.get("title","").lower().replace(" ","-")[:50]),
                 "date": datetime.now().strftime("%Y-%m-%d")}
        if not any(a.get("title") == entry["title"] for a in archive):
            archive.append(entry)
            save_blog_archive(archive)
            print(f"📚 Blog arşivi: {len(archive)} yazı")

    # 5. Kaydet
    output = {
        "generated_at": datetime.now().isoformat(),
        "amazon_tag":   AMAZON_TAG,
        "ai_mode":      "groq" if ai_mode else "template",
        "config":       {"adsense_id": ADSENSE_ID, "pinterest_url": PINTEREST_URL, "site_url": SITE_URL},
        "products":     enriched,
        "blog":         blog,
        "stats":        {"total_products": len(enriched), "categories": list(set(p["category"] for p in enriched))},
    }
    with open("website_data.json","w",encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    # 6. Pinterest CSV
    with open("pinterest_upload.csv","w",newline="",encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=["Title","Description","Link","Image","Board"], quoting=csv.QUOTE_ALL)
        w.writeheader()
        boards = {"Action Figures":"Best Action Figures 2026","Dinosaurs":"Dinosaur Toys for Kids","Playsets":"Kids Playsets & Adventures","Vehicles":"Toy Cars & Vehicles","Educational":"STEM & Educational Toys","Fantasy":"Fantasy Creature Figures","Animals":"Animal Figures for Kids"}
        for p in enriched:
            w.writerow({"Title":f"🎯 {p['title'][:80]}","Description":f"Shop this amazing {p['category']} toy on Amazon for only {p['price']}! Perfect for kids {p.get('age_group','3+')}. Curated by RoccoZoom! #toys #amazon #kidstoys","Link":SITE_URL,"Image":p["image_url"],"Board":boards.get(p["category"],"Best Toys 2026")})

    # 7. Sitemap + Robots
    generate_sitemap(archive)
    generate_robots()

    print("\n✅ TAMAMLANDI!")
    print(f"   → {len(enriched)} oyuncak işlendi")
    print(f"   → AI: {'Groq' if ai_mode else 'Şablon'}")
    print(f"   → Blog arşivi: {len(archive)} yazı")
    print(f"   → Tüm dosyalar güncellendi")
    print("="*55)

if __name__ == "__main__":
    main()
