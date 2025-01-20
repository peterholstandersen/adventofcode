import sys
import re

basedir = "/home/peter/spil/spacemaster/expanse/"

with open(basedir + "table_template.fodt") as f:
    text = f.read()

#       <text:p text:style-name="P3">03-30</text:p>
#      </table:table-cell>
#      <table:table-cell table:style-name="Table2.B4" office:value-type="string">
#       <text:p text:style-name="P2">0</text:p>
#      </table:table-cell>
#      <table:table-cell table:style-name="Table2.C4" office:value-type="string">
#       <text:p text:style-name="P2">0</text:p>
#      </table:table-cell>
#      <table:table-cell table:style-name="Table2.D4" office:value-type="string">
#       <text:p text:style-name="P2">0</text:p>
#      </table:table-cell>
#      <table:table-cell table:style-name="Table2.E4" office:value-type="string">
#       <text:p text:style-name="P2">0</text:p>
#      </table:table-cell>
#      <table:table-cell table:style-name="Table2.F4" office:value-type="string">
#       <text:p text:style-name="P2">0</text:p>

# match = re.findall(r".*>\d\d-\d\d<.*>\d<.*>\d<.*>\d<.*>\d<.*>\d<.*", text)
# match = re.findall(r".*>\d\d-\d\d<", text)

def adjust_roll(match):
    p = lambda n: f"({n})" if n < 0 else str(n)
    pre = match.group(1)
    r1 = int(match.group(2))
    r2 = int(match.group(3))
    post = match.group(4)
    n = 30
    x = pre + p(r1 - n) + "-" + p(r2 - n) + post
    return x

mk = 5

def multiply_damage(match):
    pre = match.group(1)
    dam = int(match.group(2))
    post = match.group(3)
    print(dam)
    return pre + str(dam * mk) + post

text = text.replace("NNNN", str(mk))

#       <text:p text:style-name="P3">03-30</text:p>
out = re.sub(r"(<.*>)(\d+)-(\d+)(<.*>).*", adjust_roll, text)

# <text:p text:style-name="P2">0</text:p>
out2 = re.sub(r"(<text:p text:style-name=\".*\">)(\d+)(</text:p>)", multiply_damage, out)

with open(basedir + "out.fodt", "w") as f:
    f.write(out2)
