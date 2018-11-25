import pandas as pd
import argparse

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Parse cmd args.'
    )
    parser.add_argument(
        '--date-from',
        metavar='F',
        type=str,
        help='an integer for the accumulator'
    )
    parser.add_argument(
        '--date-to',
        metavar='T',
        type=str,
        help='an integer for the accumulator'
    )
    parser.add_argument(
        'commodity',
        metavar='C',
        type=str,
        help='an integer for the accumulator'
    )
    args = parser.parse_args()

    date_range = None
    date_range_str = ""

    if not args.commodity:
        print("Please specify commodity type(solver, gold)")
        exit()

    df = pd.read_pickle('data/{}.pd'.format(args.commodity))

    if args.date_from and args.date_to and args.date_from < args.date_to:
        date_range = df.date.between(args.date_from, args.date_to)

    if date_range is not None:
        df_query = df['price'][date_range]
        date_range_str = "\n    Date from: {}\n    Date to: {}".format(args.date_from, args.date_to)
    else:
        df_query = df['price']

    output = """
    ---------------------------------
    |   Comodity: {comodity:}
    |--------------------------------
    |   Mean: {mean:.4f}
    |   Variance: {var:.4f}
    ---------------------------------{daterange}
    """.format(
        comodity=args.commodity,
        mean=df_query.mean(),
        var=df_query.var(),
        daterange=date_range_str
    )
    print(output.format())
