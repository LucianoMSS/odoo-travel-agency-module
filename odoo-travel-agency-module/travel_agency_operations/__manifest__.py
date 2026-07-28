{
    'name': 'Travel Agency Operations & Collections',
    'version': '16.0.1.0.0',
    'summary': 'Manage trips, PNR reservations, passenger details, net margin profitability, and collection reports for travel agencies.',
    'category': 'Sales/Accounting',
    'author': 'Open Source Developer',
    'license': 'LGPL-3',
    'depends': ['account', 'base'],
    'data': [
        'security/ir.model.access.csv',
        'views/trip_views.xml',
        'views/collection_views.xml',
    ],
    'installable': True,
    'application': True,
}
