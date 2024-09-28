import numpy as np
import sys
import subprocess
import re
#from typing import List, Dict
#import PyPDF4


def help():
    usage = f"""Usage: {sys.argv[0]} [input_file] [arguments]

Arguments:
    -f      Page format (supported options: A5, A6; standard value: A6)
    -p      Number of pages (standard value: number of pages of input file)"""
    return usage


def order4(pages):

    sheets = int(np.ceil(pages/4))
    pages4 = sheets*4
    pages2 = int(np.ceil(pages/2))*2
    arr = [None] * pages4
    strarr = [None] * pages4
    te = pages4  # top even
    tu = pages4-1  # top uneven
    be = 2  # bottom even
    bu = 1  # bottom uneven

    loop_start = 0

    for i in range(loop_start, sheets):
        strarr[i*4] = str(bu) + 'west'
        arr[i*4] = bu
        bu += 2
        strarr[i*4+1] = str(te) + 'west'
        arr[i*4+1] = te
        te -= 2
        strarr[i*4+2] = str(be) + 'east'
        arr[i*4+2] = be
        be += 2
        strarr[i*4+3] = str(tu) + 'east'
        arr[i*4+3] = tu
        tu -= 2

    for i in range(0, pages4):
        if (arr[i] > pages):
            strarr[i] = 'B1'
        else:
            strarr[i] = 'A' + strarr[i]

    string = ' '.join(strarr)
    return string



def order8(pages):

    sheets = int(np.ceil(pages/8))
    pages8 = sheets*8
    pages4 = int(np.ceil(pages/4))*4
    arr = [None] * pages8
    strarr = [None] * pages8
    te = pages8  # top even
    tu = pages8-1  # top uneven
    be = 2  # bottom even
    bu = 1  # bottom uneven

    loop_start = 0

    if (pages4 != pages8):
        te -= 4
        tu -= 4

        strarr[0] = str(te)
        arr[0] = te
        te -= 2
        strarr[1] = str(bu)
        arr[1] = bu
        bu += 2
        strarr[2] = str(tu + 4)
        arr[2] = tu + 4
        strarr[3] = str(te + 6)
        arr[3] = te + 6
        strarr[4] = str(be)
        arr[4] = be
        be += 2
        strarr[5] = str(tu)
        arr[5] = tu
        tu -= 2
        strarr[6] = str(tu + 4)
        arr[6] = tu + 4
        strarr[7] = str(te + 4)
        arr[7] = te + 4
        loop_start = 1

    for i in range(loop_start, sheets):
        strarr[i*8] = str(te)
        arr[i*8] = te
        te -= 2
        strarr[i*8+1] = str(bu)
        arr[i*8+1] = bu
        bu += 2
        strarr[i*8+2] = str(bu) + 'south'
        arr[i*8+2] = bu
        bu += 2
        strarr[i*8+3] = str(te) + 'south'
        arr[i*8+3] = te
        te -= 2
        strarr[i*8+4] = str(be)
        arr[i*8+4] = be
        be += 2
        strarr[i*8+5] = str(tu)
        arr[i*8+5] = tu
        tu -= 2
        strarr[i*8+6] = str(tu) + 'south'
        arr[i*8+6] = tu
        tu -= 2
        strarr[i*8+7] = str(be) + 'south'
        arr[i*8+7] = be
        be += 2

    for i in range(0, pages8):
        if (arr[i] > pages):
            strarr[i] = 'B1'
        else:
            strarr[i] = 'A' + strarr[i]

    string = ' '.join(strarr)
    return string



def main():
    opts = [opt for opt in sys.argv[1:] if opt.startswith("-")]
    args = [arg for arg in sys.argv[1:] if (not arg.startswith("-") and arg!='')]

    if "-h" in opts or "--help" in opts:
        print(help())
        return
    elif len(args)!=len(opts)+1:
        raise SystemExit("Invalid input.\n" + help())

    if "-f" in opts:
        page_format = args[opts.index("-f")+1]
    elif "--form" in opts:
        page_format = args[opts.index("--form")+1]
    else:
        page_format = "A6"

    filename = args[0]
    command00 = 'pdftk ' + filename + ' dump_data'
    process = subprocess.Popen(command00.split(), stdout=subprocess.PIPE)
    output, error = process.communicate()

    pages_r = re.search(r"NumberOfPages: (\d*)", str(output))
    read_pages = int(pages_r[1])

    if "-p" in opts:
        pages = int(args[opts.index("-p")+1])
    elif "--pages" in opts:
        pages = int(args[opts.index("--pages")+1])
    else:
        pages = read_pages


    if (page_format == "A6"):
        filename2 = filename.replace('.pdf', '') + '_2x2'
        string = order8(pages)
        command0 = 'convert xc:none -page A6 b.pdf'
        # align in 2x2 grid
        command2 = 'pdfjam --nup 2x2 ' + filename + '_temprot.pdf --outfile ' + filename2 + '.pdf --paper a4paper'
    elif (page_format == "A5"):
        filename2 = filename.replace('.pdf', '') + '_1x2'
        string = order4(pages)
        command0 = 'convert xc:none -page A5 b.pdf'
        # align in 1x2 grid
        command2 = 'pdfjam --nup 1x2 ' + filename + '_temprot.pdf --outfile ' + filename2 + '.pdf --paper a4paper'
    else:
        raise SystemExit("Unsupported page format.\n" + help())

    print(string)
    # create blank pdf
    process = subprocess.Popen(command0.split(), stdout=subprocess.PIPE)
    output, error = process.communicate()

    # rotate pages and add blank pages
    command1 = 'pdftk A=' + filename + ' B=b.pdf cat ' + string + ' output ' + filename + '_temprot.pdf'
    process = subprocess.Popen(command1.split(), stdout=subprocess.PIPE)
    output, error = process.communicate()

    # align in 2x2 grid
    process = subprocess.Popen(command2.split(), stdout=subprocess.PIPE)
    output, error = process.communicate()

    # remove temporal rotated file
    command3 = 'rm -f ' + filename + '_temprot.pdf b.pdf'
    process = subprocess.Popen(command3.split(), stdout=subprocess.PIPE)
    output, error = process.communicate()


if __name__ == '__main__':
    main()
