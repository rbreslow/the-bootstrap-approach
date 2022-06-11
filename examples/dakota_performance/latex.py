# noinspection PyProtectedMember
from tabulate import TableFormat, partial, _latex_line_begin_tabular, Line, _latex_row

TABLE_FORMAT: TableFormat = TableFormat(
    lineabove=partial(_latex_line_begin_tabular, booktabs=True, longtable=True),
    linebelowheader=Line("\\midrule", "", "", ""),
    linebetweenrows=None,
    linebelow=Line("\\bottomrule\n\\end{longtable}", "", "", ""),
    headerrow=partial(_latex_row, escrules={}),
    datarow=_latex_row,
    padding=1,
    with_header_hide=None,
)
