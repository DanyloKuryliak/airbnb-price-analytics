"""Build the AI/BI (Lakeview) dashboard definition from dashboard/datasets/*.sql.

Usage:
    python scripts/build_dashboard.py [--catalog workspace] [--gold-schema airbnb_gold]

Writes dashboard/airbnb_price_analytics.lvdash.json, which is imported in Databricks via
Dashboards > Create dashboard > Import dashboard from file. Page headlines are kept in
PAGE_HEADLINES; update them from measured results before publication.
"""
import argparse
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATASET_DIR = ROOT / 'dashboard' / 'datasets'
OUTPUT = ROOT / 'dashboard' / 'airbnb_price_analytics.lvdash.json'
SOURCE_NAMESPACE = 'workspace.airbnb_gold'

# Headlines state a finding (assignment requirement). Overview and comparison values come from the
# EDA run of 2026-11-09 (docs/eda_findings.md) and were verified on the deployed dashboard; model
# values come from docs/model_results.md and v_model_performance (model v1, Greater Manchester
# first_run). Verify them after every rerun.
# Settings exported by Databricks, preserved when the definition is regenerated.
UI_SETTINGS = {'theme': {'widgetHeaderAlignment': 'ALIGNMENT_UNSPECIFIED'}, 'applyModeEnabled': False}
PAGE_HEADLINES = {
    'overview': (
        '## London has 31 times more listings than Bristol, and its median night costs £175 against £130',
        'Nightly advertised prices in GBP on the snapshot date. Price statistics use listings with a valid '
        'price only; about one in three London listings and nearly one in four Bristol listings advertise no '
        'price. '
        'Availability counts open calendar days and is not occupancy.',
    ),
    'comparison': (
        '## Bristol is about a quarter cheaper than London and stays open roughly 50 more days a year',
        'Differences are shown against London. Compare the same room type and guest capacity before '
        'reading the overall gap, because the cities differ in room-type composition and listing size.',
    ),
    'model': (
        '## On unseen Greater Manchester the unchanged model scores £79.68 MAE: close to £76.93 on London + '
        'Bristol and 21% better than the £100.84 baseline',
        'Model v1, unchanged first run (run first_run): 7,799 Manchester listings scored (100% coverage), 6,692 '
        'with a valid price evaluated. London + Bristol: held-out test split, 12,434 listings, model £76.93 '
        'against baseline £104.17 (26% better). The baseline transfers worse than the model: its median '
        'absolute error rises from £44.84 to £73.50. Error = predicted - actual; negative means the model '
        'under-prices. Baseline = training median for the same room type and guest capacity. Filter by run to '
        'compare the first run with later fixes.',
    ),
}


# Data-storytelling style (Lecture 7): grey context, one saturated accent for the subject of the
# widget title, direct labels instead of legends, value-sorted categories, no pence.
GREY = '#A3A3A3'
ACCENT = '#2F6FD6'
GBP0 = {'type': 'number-currency', 'currencyCode': 'GBP', 'decimalPlaces': {'type': 'exact', 'places': 0}}
GBP2 = {'type': 'number-currency', 'currencyCode': 'GBP', 'decimalPlaces': {'type': 'exact', 'places': 2}}
NUM0 = {'type': 'number-plain', 'decimalPlaces': {'type': 'exact', 'places': 0}}
NUM1 = {'type': 'number-plain', 'decimalPlaces': {'type': 'max', 'places': 1}}
NUM2 = {'type': 'number-plain', 'decimalPlaces': {'type': 'max', 'places': 2}}
PCT1 = {'type': 'number-plain', 'decimalPlaces': {'type': 'max', 'places': 1}, 'suffix': '%'}

CITIES = ['London', 'Bristol', 'Greater Manchester']
AB_FILTER = "`city_name` IN ('London', 'Bristol')"
GM_FILTER = "`city_name` = 'Greater Manchester'"
MAIN_ROOM_TYPES = "`room_type` IN ('Entire home/apt', 'Private room')"
GUEST_ORDER = ['1', '2', '3', '4', '5', '6', '7', '8+']
# Ten Manchester neighbourhoods with the highest first-run MAE (title_facts.sql, section E).
GM_TOP_ERROR_NEIGHBOURHOODS = ['Ardwick', 'Bradford', 'Ancoats and Clayton', 'Burnage', 'Tameside District',
                               'Harpurhey', 'Hulme', 'Moston', 'Gorton South', 'Crumpsall']
BAND_ORDER = ['under £50', '£50-99', '£100-149', '£150-199', '£200-299', '£300-499', '£500-999', '£1,000+']

# Titles that need a value not yet recorded in the repository. They are replaced from the
# title-facts query (see dashboard/README.md) before publication; main() lists them.
PENDING = '[title pending] '


def accent(subject, values):
    """Colour mapping: the title subject in the accent colour, every other value grey."""
    return [{'value': v, 'color': ACCENT if v == subject else GREY} for v in values]


def field(name):
    return {'name': name, 'expression': f'`{name}`'}


def query(dataset, columns, filters=None):
    q = {'datasetName': dataset, 'fields': [field(c) for c in columns], 'disaggregated': True}
    if filters:
        q['filters'] = [{'expression': f} for f in filters]
    return [{'name': 'main_query', 'query': q}]


def frame(title, description=None):
    out = {'showTitle': True, 'title': title}
    if description:
        out.update(showDescription=True, description=description)
    return out


def bar(name, dataset, category, measure, title, *, horizontal=True, fmt=None, color=None,
        mappings=None, order=None, group=False, filters=None, description=None):
    """Value-sorted bar chart with data labels and no legend.

    category/measure/color are (field, label). The category axis is sorted by value unless an
    ordinal order is given; colours come only from explicit grey/accent mappings.
    """
    cat_scale = {'type': 'categorical'}
    if order:
        cat_scale['sort'] = {'by': 'custom-order', 'orderedValues': order}
    else:
        cat_scale['sort'] = {'by': 'x-reversed' if horizontal else 'y-reversed'}
    cat = {'fieldName': category[0], 'displayName': category[1], 'scale': cat_scale,
           'axis': {'hideTitle': True}}
    val = {'fieldName': measure[0], 'displayName': measure[1], 'scale': {'type': 'quantitative'},
           'axis': {'hideTitle': True}}
    if fmt:
        val['format'] = fmt
    encodings = {'x': val, 'y': cat} if horizontal else {'x': cat, 'y': val}
    columns = [category[0], measure[0]]
    if color:
        encodings['color'] = {'fieldName': color[0], 'displayName': color[1],
                              'scale': {'type': 'categorical', 'mappings': mappings or []},
                              'legend': {'hide': True}}
        columns.append(color[0])
    encodings['label'] = {'show': True}
    spec = {'version': 3, 'widgetType': 'bar', 'encodings': encodings, 'frame': frame(title, description)}
    if group:
        spec['mark'] = {'layout': 'group'}
    return {'name': name, 'queries': query(dataset, list(dict.fromkeys(columns)), filters), 'spec': spec}


def scatter(name, dataset, x, y, title, color, mappings, description=None):
    encodings = {
        'x': {'fieldName': x[0], 'displayName': x[1], 'scale': {'type': 'quantitative'}, 'format': GBP0},
        'y': {'fieldName': y[0], 'displayName': y[1], 'scale': {'type': 'quantitative'}, 'format': GBP0},
        'color': {'fieldName': color[0], 'displayName': color[1],
                  'scale': {'type': 'categorical', 'mappings': mappings}, 'legend': {'hide': True}},
    }
    return {'name': name, 'queries': query(dataset, [x[0], y[0], color[0]]),
            'spec': {'version': 3, 'widgetType': 'scatter', 'encodings': encodings,
                     'frame': frame(title, description)}}


def table(name, dataset, columns, title, description=None, filters=None):
    """columns: list of (field, label, format or None)."""
    specs = []
    for col, label, fmt in columns:
        spec = {'fieldName': col, 'displayName': label}
        if fmt:
            spec['format'] = fmt
        specs.append(spec)
    return {'name': name, 'queries': query(dataset, [c[0] for c in columns], filters),
            'spec': {'version': 2, 'widgetType': 'table',
                     'encodings': {'columns': specs},
                     'frame': frame(title, description)}}


def multi_filter(name, column, label, datasets):
    queries = [{'name': f'{name}_{ds}',
                'query': {'datasetName': ds, 'fields': [field(column)], 'disaggregated': False}}
               for ds in datasets]
    return {'name': name, 'queries': queries,
            'spec': {'version': 2, 'widgetType': 'filter-multi-select',
                     'encodings': {'fields': [{'fieldName': column, 'displayName': label, 'queryName': q['name']}
                                              for q in queries]},
                     'frame': frame(label)}}


def text(name, lines):
    return {'name': name, 'multilineTextboxSpec': {'lines': lines}}


def place(widget, x, y, w, h):
    return {'widget': widget, 'position': {'x': x, 'y': y, 'width': w, 'height': h}}


def headline(page):
    title, body = PAGE_HEADLINES[page]
    return place(text(f'{page}_headline', [title + '\n', '\n', body]), 0, 0, 6, 2)


def overview_page():
    ds = ['city_overview', 'room_type_mix', 'top_neighbourhoods']
    city = ('city_name', 'City')
    return [
        headline('overview'),
        place(multi_filter('overview_city', 'city_name', 'City', ds), 0, 2, 2, 1),
        place(table('overview_table', 'city_overview', [
            ('city_name', 'City', None), ('snapshot_date', 'Snapshot', None),
            ('total_listings', 'Listings', NUM0), ('valid_price_listings', 'With valid price', NUM0),
            ('price_coverage_pct', 'Price coverage', PCT1), ('median_price_gbp', 'Median price', GBP0),
            ('median_availability_365', 'Median available days /365', NUM0),
            ('avg_review_score', 'Mean rating (0-5)', NUM2), ('review_listings', 'Rated listings', NUM0),
            ('distinct_hosts', 'Hosts', NUM0), ('listings_per_host', 'Listings per host', NUM2),
            ('entire_home_share_pct', 'Entire homes', PCT1), ('neighbourhoods', 'Neighbourhoods', NUM0),
        ], 'Mean ratings barely differ between cities (4.67-4.76); the table keeps every denominator'),
              0, 3, 6, 3),
        place(bar('overview_price', 'city_overview', city, ('median_price_gbp', 'Median nightly price'),
                  "London's median night costs £175, against £130 in Bristol and £117 in Greater Manchester",
                  fmt=GBP0, color=city, mappings=accent('London', CITIES)), 0, 6, 2, 5),
        place(bar('overview_availability', 'city_overview', city,
                  ('median_availability_365', 'Median available days'),
                  "Greater Manchester listings are open 267 days a year, more than twice London's 120",
                  fmt=NUM0, color=city, mappings=accent('Greater Manchester', CITIES),
                  description='Open calendar days in the next 365; not occupancy.'), 2, 6, 2, 5),
        place(bar('overview_hosts', 'city_overview', city, ('listings_per_host', 'Listings per host'),
                  'Manchester hosts run the most listings each: 2.11, against 1.79 in London and 1.67 in Bristol',
                  fmt=NUM2, color=city, mappings=accent('Greater Manchester', CITIES)), 4, 6, 2, 5),
        place(bar('overview_entire_share', 'room_type_mix', city, ('share_pct', 'Entire-home share'),
                  'Entire homes are two-thirds of listings in every city, most in Bristol (72%)',
                  fmt=PCT1, color=city, mappings=accent('Bristol', CITIES),
                  filters=["`room_type` = 'Entire home/apt'"],
                  description='Share of listings that are entire homes; hotel and shared rooms are under 1%.'),
              0, 11, 2, 8),
        place(bar('overview_neighbourhoods', 'top_neighbourhoods', ('neighbourhood', 'Neighbourhood'),
                  ('median_price_gbp', 'Median nightly price'),
                  "Westminster is London's most expensive neighbourhood at £282 a night, just ahead of the "
                  'City of London (£278)',
                  fmt=GBP0, color=city, mappings=accent('London', CITIES),
                  filters=["`city_name` = 'London'"],
                  description='Median nightly price; neighbourhoods with at least 10 valid prices.'),
              2, 11, 4, 8),
    ]


def comparison_page():
    city = ('city_name', 'City')
    ab = ['London', 'Bristol']
    legend_note = 'Blue: Bristol. Grey: London.'
    return [
        headline('comparison'),
        place(table('comparison_table', 'city_comparison', [
            ('metric', 'Metric', None), ('unit', 'Unit', None), ('city_name', 'City', None),
            ('value', 'Value', NUM2), ('difference_vs_reference', 'Difference vs London', NUM2),
            ('pct_difference_vs_reference', 'Difference vs London', PCT1),
        ], 'Bristol trails London on every price measure but is open more days', filters=[AB_FILTER]),
              0, 2, 3, 8),
        place(bar('comparison_room_price', 'room_type_mix', ('room_type', 'Room type'),
                  ('median_price_gbp', 'Median nightly price'),
                  "A Bristol entire home costs £158 a night, £69 less than London's £227",
                  horizontal=False, fmt=GBP0, color=city, mappings=accent('Bristol', ab), group=True,
                  filters=[AB_FILTER, MAIN_ROOM_TYPES],
                  description=legend_note + ' Private rooms: £60 against £80.'), 3, 2, 3, 8),
        place(bar('comparison_capacity', 'capacity_prices', ('guests', 'Guests'),
                  ('median_price_gbp', 'Median nightly price'),
                  "London's premium over Bristol grows with group size: £23 for 2 guests, £68 for 4",
                  horizontal=False, fmt=GBP0, color=city, mappings=accent('Bristol', ab), group=True,
                  order=GUEST_ORDER, filters=[AB_FILTER], description=legend_note), 0, 10, 3, 7),
        place(bar('comparison_bands', 'price_bands', ('price_band', 'Nightly price band'),
                  ('share_pct', 'Share of priced listings'),
                  '52% of Bristol listings cost £50-149 a night, against 38% in London',
                  horizontal=False, fmt=PCT1, color=city, mappings=accent('Bristol', ab), group=True,
                  order=BAND_ORDER, filters=[AB_FILTER], description=legend_note), 3, 10, 3, 7),
    ]


def model_page():
    ds = ['model_mae', 'model_performance', 'predicted_vs_actual', 'error_by_room_type',
          'error_by_neighbourhood', 'largest_errors']
    city = ('city_name', 'City')
    estimators = ['Baseline: median by room type and guests', 'Model']
    return [
        headline('model'),
        place(multi_filter('model_city', 'city_name', 'City', ds), 0, 2, 2, 1),
        place(multi_filter('model_version', 'model_version', 'Model version', ds), 2, 2, 2, 1),
        place(multi_filter('model_run', 'run_label', 'Run', ds), 4, 2, 2, 1),
        place(bar('model_mae_chart', 'model_mae', city, ('mae_gbp', 'MAE'),
                  "In Manchester the model's MAE is £79.68 against £100.84 for the baseline",
                  horizontal=False, fmt=GBP0, color=('estimator', 'Estimator'),
                  mappings=accent('Model', estimators), group=True,
                  description='Blue: model. Grey: baseline. London and Bristol: test split; '
                              'Manchester: unchanged first run.'), 0, 3, 3, 7),
        place(table('model_metrics_table', 'model_performance', [
            ('city_name', 'City', None), ('model_version', 'Model', None),
            ('run_label', 'Run', None), ('evaluation_role', 'Set', None),
            ('listings_in_set', 'Listings', NUM0), ('prediction_coverage_pct', 'Coverage', PCT1),
            ('model_evaluated_listings', 'Evaluated', NUM0), ('baseline_mae_gbp', 'Baseline MAE', GBP2),
            ('model_mae_gbp', 'Model MAE', GBP2), ('mae_improvement_pct', 'Improvement', PCT1),
            ('baseline_median_abs_error_gbp', 'Baseline median AE', GBP2),
            ('model_median_abs_error_gbp', 'Model median AE', GBP2),
        ], "Manchester's typical error rises by a third (median £43.38 against £32.31), more than its MAE"),
              3, 3, 3, 7),
        place(scatter('model_scatter', 'predicted_vs_actual',
                      ('actual_price_gbp', 'Actual price'), ('predicted_price_gbp', 'Predicted price'),
                      'The model overprices 78% of Manchester listings, against about half in London and Bristol',
                      city, accent('Greater Manchester', CITIES),
                      description='Blue: Greater Manchester. Grey: London and Bristol. Points above the '
                                  'diagonal are overpriced; actual prices up to £1,000.'), 0, 10, 3, 8),
        place(bar('model_room_error', 'error_by_room_type', ('room_type', 'Room type'),
                  ('model_mae_gbp', 'Model MAE'),
                  "Entire homes carry Manchester's largest error: £100 MAE, against £37 for private rooms",
                  fmt=GBP0, color=('room_type', 'Room type'),
                  mappings=accent('Entire home/apt', ['Entire home/apt', 'Private room', 'Hotel room',
                                                       'Shared room']),
                  filters=[GM_FILTER]), 3, 10, 3, 8),
        place(bar('model_neighbourhood_error', 'error_by_neighbourhood', ('neighbourhood', 'Neighbourhood'),
                  ('model_mae_gbp', 'Model MAE'),
                  "Ardwick has Manchester's highest error: £162 MAE across 139 listings",
                  fmt=GBP0, color=('neighbourhood', 'Neighbourhood'),
                  mappings=accent('Ardwick', GM_TOP_ERROR_NEIGHBOURHOODS), filters=[GM_FILTER],
                  description='Ten neighbourhoods with the highest model MAE; at least 20 evaluated listings.'),
              0, 18, 3, 10),
        place(table('model_largest_errors', 'largest_errors', [
            ('city_name', 'City', None), ('pricing_direction', 'Direction', None),
            ('listing_id', 'Listing ID', None), ('room_type', 'Room type', None),
            ('neighbourhood', 'Neighbourhood', None), ('accommodates', 'Guests', NUM0),
            ('actual_price_gbp', 'Actual', GBP0), ('predicted_price_gbp', 'Predicted', GBP0),
            ('model_error_gbp', 'Error', GBP0),
        ], 'The worst under-pricing comes from London listings advertised at about £10,000 a night',
            'Error = predicted - actual; ten largest per city and direction. Six London listings priced '
            '£9,925-£10,163 were predicted at £155-£861 (docs/model_results.md).'),
              3, 18, 3, 10),
    ]


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('--catalog', default='workspace')
    parser.add_argument('--gold-schema', default='airbnb_gold')
    args = parser.parse_args()
    for value in (args.catalog, args.gold_schema):
        if not re.fullmatch(r'[A-Za-z][A-Za-z0-9_]*', value):
            raise ValueError(f'Invalid identifier: {value!r}')
    namespace = f'{args.catalog}.{args.gold_schema}'

    datasets = []
    for path in sorted(DATASET_DIR.glob('*.sql')):
        sql = path.read_text(encoding='utf-8').replace(SOURCE_NAMESPACE, namespace)
        lines = [line for line in sql.splitlines() if not line.startswith('--')]
        datasets.append({'name': path.stem, 'displayName': path.stem.replace('_', ' ').capitalize(),
                         'queryLines': [line + '\n' for line in lines]})
    names = {d['name'] for d in datasets}

    pages = [
        {'name': 'city_overview', 'displayName': 'City overview', 'layout': overview_page()},
        {'name': 'cross_city', 'displayName': 'London vs Bristol', 'layout': comparison_page()},
        {'name': 'model', 'displayName': 'Model', 'layout': model_page()},
    ]
    widget_names = []
    for page in pages:
        page['pageType'] = 'PAGE_TYPE_CANVAS'
        for item in page['layout']:
            widget_names.append(item['widget']['name'])
            for q in item['widget'].get('queries', []):
                if q['query']['datasetName'] not in names:
                    raise ValueError(f"Unknown dataset {q['query']['datasetName']}")
    if len(widget_names) != len(set(widget_names)):
        raise ValueError('Duplicate widget names')
    pending = [item['widget']['spec']['frame']['title'] for page in pages for item in page['layout']
               if item['widget'].get('spec', {}).get('frame', {}).get('title', '').startswith(PENDING)]

    OUTPUT.write_text(json.dumps({'datasets': datasets, 'pages': pages, 'uiSettings': UI_SETTINGS}, ensure_ascii=False, indent=2) + '\n',
                      encoding='utf-8')
    print(f'Wrote {OUTPUT.relative_to(ROOT)}: {len(datasets)} datasets, {len(pages)} pages, '
          f'{len(widget_names)} widgets, namespace {namespace}')
    for title in pending:
        print('WARNING pending title:', title)


if __name__ == '__main__':
    main()
