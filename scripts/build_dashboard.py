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
# values come from docs/model_results.md (model v1). Verify them after every rerun.
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
        '## The model cuts test-set error by 26%: £76.93 MAE against £104.17 for the baseline',
        'London + Bristol test split (12,434 listings, 100% coverage), model v1. The gain is 43% in Bristol '
        'and 26% in London, where a few listings advertised at about £5,000-£10,000 a night dominate the '
        'largest errors; the median absolute error (£32 against £45) is unaffected by them. Error = '
        'predicted - actual; negative means the model under-prices. Baseline = training median for the '
        'same room type and guest capacity. For the transfer city, filter by run: first_run is the '
        'unchanged model, later runs follow recorded fixes.',
    ),
}


def field(name):
    return {'name': name, 'expression': f'`{name}`'}


def query(dataset, columns):
    return [{'name': 'main_query',
             'query': {'datasetName': dataset, 'fields': [field(c) for c in columns], 'disaggregated': True}}]


def frame(title, description=None):
    out = {'showTitle': True, 'title': title}
    if description:
        out.update(showDescription=True, description=description)
    return out


def axis(name, title, kind, sort=False):
    enc = {'fieldName': name, 'displayName': title, 'scale': {'type': kind}}
    if sort:
        enc['scale']['sort'] = {'by': 'natural-order'}
    return enc


def chart(name, dataset, kind, x, y, title, color=None, group=False, description=None):
    """Bar or scatter chart; x/y/color are (field, label, scale type[, natural sort])."""
    columns = [x[0], y[0]] + ([color[0]] if color else [])
    encodings = {'x': axis(*x), 'y': axis(*y)}
    if color:
        encodings['color'] = axis(*color)
    spec = {'version': 3, 'widgetType': kind, 'encodings': encodings, 'frame': frame(title, description)}
    if group:
        spec['mark'] = {'layout': 'group'}
    return {'name': name, 'queries': query(dataset, columns), 'spec': spec}



def table(name, dataset, columns, title, description=None):
    """columns: list of (field, label, type); type documents the column and is not exported."""
    specs = [{'fieldName': col, 'displayName': label} for col, label, _ in columns]
    return {'name': name, 'queries': query(dataset, [c[0] for c in columns]),
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
    return [
        headline('overview'),
        place(multi_filter('overview_city', 'city_name', 'City', ds), 0, 2, 2, 1),
        place(table('overview_table', 'city_overview', [
            ('city_name', 'City', 'string'), ('snapshot_date', 'Snapshot', 'date'),
            ('total_listings', 'Listings', 'int'), ('valid_price_listings', 'With valid price', 'int'),
            ('price_coverage_pct', 'Price coverage %', 'float'), ('median_price_gbp', 'Median price £', 'float'),
            ('median_availability_365', 'Median available days /365', 'float'),
            ('avg_review_score', 'Mean rating (0-5)', 'float'), ('review_listings', 'Rated listings', 'int'),
            ('distinct_hosts', 'Hosts', 'int'), ('listings_per_host', 'Listings per host', 'float'),
            ('entire_home_share_pct', 'Entire homes %', 'float'), ('neighbourhoods', 'Neighbourhoods', 'int'),
        ], 'Headline metrics per city with denominators'), 0, 3, 6, 3),
        place(chart('overview_price', 'city_overview', 'bar', ('city_name', 'City', 'categorical'),
                    ('median_price_gbp', 'Median nightly price (£)', 'quantitative'),
                    'Median nightly advertised price', color=('city_name', 'City', 'categorical')), 0, 6, 2, 5),
        place(chart('overview_availability', 'city_overview', 'bar', ('city_name', 'City', 'categorical'),
                    ('median_availability_365', 'Median available days', 'quantitative'),
                    'Median available days in the next 365 (not occupancy)',
                    color=('city_name', 'City', 'categorical')), 2, 6, 2, 5),
        place(chart('overview_reviews', 'city_overview', 'bar', ('city_name', 'City', 'categorical'),
                    ('avg_review_score', 'Mean rating (0-5)', 'quantitative'),
                    'Mean overall review score among rated listings',
                    color=('city_name', 'City', 'categorical')), 4, 6, 2, 5),
        place(chart('overview_room_mix', 'room_type_mix', 'bar', ('city_name', 'City', 'categorical'),
                    ('share_pct', 'Share of listings (%)', 'quantitative'), 'Room-type mix',
                    color=('room_type', 'Room type', 'categorical')), 0, 11, 2, 8),
        place(chart('overview_hosts', 'city_overview', 'bar', ('city_name', 'City', 'categorical'),
                    ('listings_per_host', 'Listings per host', 'quantitative'),
                    'Listings per host (multi-listing hosts)', color=('city_name', 'City', 'categorical')),
              0, 19, 2, 5),
        place(chart('overview_neighbourhoods', 'top_neighbourhoods', 'bar',
                    ('median_price_gbp', 'Median nightly price (£)', 'quantitative'),
                    ('neighbourhood', 'Neighbourhood', 'categorical'),
                    'Most expensive neighbourhoods (at least 10 valid prices)',
                    color=('city_name', 'City', 'categorical')), 2, 11, 4, 13),
    ]


def comparison_page():
    return [
        headline('comparison'),
        place(table('comparison_table', 'city_comparison', [
            ('metric', 'Metric', 'string'), ('unit', 'Unit', 'string'), ('city_name', 'City', 'string'),
            ('value', 'Value', 'float'), ('difference_vs_reference', 'Difference vs London', 'float'),
            ('pct_difference_vs_reference', 'Difference vs London %', 'float'),
        ], 'Side-by-side metrics'), 0, 2, 3, 9),
        place(chart('comparison_room_price', 'room_type_mix', 'bar', ('room_type', 'Room type', 'categorical'),
                    ('median_price_gbp', 'Median nightly price (£)', 'quantitative'),
                    'Same room type, different price level', color=('city_name', 'City', 'categorical'),
                    group=True), 3, 2, 3, 9),
        place(chart('comparison_capacity', 'capacity_prices', 'bar',
                    ('guests', 'Guests', 'categorical', True),
                    ('median_price_gbp', 'Median nightly price (£)', 'quantitative'),
                    'Median price rises with guest capacity in both cities',
                    color=('city_name', 'City', 'categorical'), group=True), 0, 11, 3, 7),
        place(chart('comparison_bands', 'price_bands', 'bar',
                    ('price_band', 'Nightly price band', 'categorical', True),
                    ('share_pct', 'Share of priced listings (%)', 'quantitative'),
                    'Price distribution', color=('city_name', 'City', 'categorical'), group=True), 3, 11, 3, 7),
        place(chart('comparison_room_share', 'room_type_mix', 'bar', ('room_type', 'Room type', 'categorical'),
                    ('share_pct', 'Share of listings (%)', 'quantitative'), 'Room-type composition',
                    color=('city_name', 'City', 'categorical'), group=True), 0, 18, 6, 6),
    ]


def model_page():
    ds = ['model_mae', 'model_performance', 'predicted_vs_actual', 'error_by_room_type',
          'error_by_neighbourhood', 'largest_errors']
    return [
        headline('model'),
        place(multi_filter('model_city', 'city_name', 'City', ds), 0, 2, 2, 1),
        place(multi_filter('model_version', 'model_version', 'Model version', ds), 2, 2, 2, 1),
        place(multi_filter('model_run', 'run_label', 'Run', ds), 4, 2, 2, 1),
        place(chart('model_mae_chart', 'model_mae', 'bar', ('city_name', 'City', 'categorical'),
                    ('mae_gbp', 'MAE (£)', 'quantitative'), 'Test-set MAE: model against baseline',
                    color=('estimator', 'Estimator', 'categorical'), group=True), 0, 3, 3, 7),
        place(table('model_metrics_table', 'model_performance', [
            ('city_name', 'City', 'string'), ('model_version', 'Model', 'string'),
            ('run_label', 'Run', 'string'), ('evaluation_role', 'Set', 'string'),
            ('listings_in_set', 'Listings', 'int'), ('prediction_coverage_pct', 'Coverage %', 'float'),
            ('model_evaluated_listings', 'Evaluated', 'int'), ('baseline_mae_gbp', 'Baseline MAE £', 'float'),
            ('model_mae_gbp', 'Model MAE £', 'float'), ('mae_improvement_pct', 'Improvement %', 'float'),
            ('baseline_median_abs_error_gbp', 'Baseline median AE £', 'float'),
            ('model_median_abs_error_gbp', 'Model median AE £', 'float'),
        ], 'MAE with denominators and coverage'), 3, 3, 3, 7),
        place(chart('model_scatter', 'predicted_vs_actual', 'scatter',
                    ('actual_price_gbp', 'Actual price (£)', 'quantitative'),
                    ('predicted_price_gbp', 'Predicted price (£)', 'quantitative'),
                    'Predicted against actual price (actual up to £1,000)',
                    color=('city_name', 'City', 'categorical')), 0, 10, 3, 8),
        place(chart('model_room_error', 'error_by_room_type', 'bar', ('room_type', 'Room type', 'categorical'),
                    ('model_mae_gbp', 'Model MAE (£)', 'quantitative'), 'Error by room type',
                    color=('city_name', 'City', 'categorical'), group=True), 3, 10, 3, 8),
        place(chart('model_neighbourhood_error', 'error_by_neighbourhood', 'bar',
                    ('model_mae_gbp', 'Model MAE (£)', 'quantitative'),
                    ('neighbourhood', 'Neighbourhood', 'categorical'),
                    'Neighbourhoods with the highest error (at least 20 evaluated listings)',
                    color=('city_name', 'City', 'categorical')), 0, 18, 3, 10),
        place(table('model_largest_errors', 'largest_errors', [
            ('city_name', 'City', 'string'), ('run_label', 'Run', 'string'),
            ('pricing_direction', 'Direction', 'string'),
            ('listing_id', 'Listing ID', 'string'), ('room_type', 'Room type', 'string'),
            ('neighbourhood', 'Neighbourhood', 'string'), ('accommodates', 'Guests', 'int'),
            ('actual_price_gbp', 'Actual £', 'float'), ('predicted_price_gbp', 'Predicted £', 'float'),
            ('model_error_gbp', 'Error £', 'float'),
        ], 'Most under- and over-priced listings', 'Error = predicted - actual.'), 3, 18, 3, 10),
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

    OUTPUT.write_text(json.dumps({'datasets': datasets, 'pages': pages, 'uiSettings': UI_SETTINGS}, ensure_ascii=False, indent=2) + '\n',
                      encoding='utf-8')
    print(f'Wrote {OUTPUT.relative_to(ROOT)}: {len(datasets)} datasets, {len(pages)} pages, '
          f'{len(widget_names)} widgets, namespace {namespace}')


if __name__ == '__main__':
    main()
