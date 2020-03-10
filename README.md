![PacketBuilder example](https://i.imgur.com/T8BixQk.png "PacketBuilder example")


# PacketBuilder
Converts qems output csv files into packetized pdfs

## Instructions

Download the repository. Add your qems output csv and update the settings.txt file to reflect your qems output filename and the name of your set. Install pandas and pdflatex. Run the Python script.

The program will generate pdf packet files but also the .tex files, which can be used to correct imperfections.

## Sprinkling Algorithm

The script will generate p = q / 20 packets, where q is the number of tossups/bonuses.

The tossups are divided into __categories__ based on the listed category and __major categories__ based on the first word of their category. Any category with more than p tossups has 1 randomly selected tossup placed into each packet. This is repeated until all categories have fewer the p tossups, at which point the remaining tossups are pooled into major categories and shuffled. With this new list of "excess tossups," one tossup at a time is placed into each packet until all of the packets are full. This process is then repeated for bonuses.

## Randomization Algorithm

Based on [common principles of packetization](https://hsquizbowl.org/forums/viewtopic.php?f=117&t=21067&sid=fd31899bf7bb3026f7cec1e5758c3229), the tossups and bonuses within each packet are shuffled randomly until they fulfill the following criteria:

1. No tossup has the same major category as the bonus at the same position.

2. No major category should appear in two consecutive tossups or in two consecutive bonuses.

3. The last tossup should not be geography, current events, or trash.

To avoid running forever, criterion 3 is abandoned after 1500 attempts, criterion 2 after 2000 attempts, and criterion 1 after 2500 attempts.
