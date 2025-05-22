from django.contrib.auth.management.commands import createsuperuser
from django.core.management import CommandError
from django.utils.translation import gettext as _


class Command(createsuperuser.Command):

    def add_arguments(self, parser):
        super().add_arguments(parser)
        parser.add_argument('--first_name', required=True, help='first name')
        parser.add_argument('--last_name', required=True, help='last name')

    def handle(self, *args, **options):
        first_name = options.get('first_name')
        last_name = options.get('last_name')

        if not first_name or not last_name:
            raise CommandError(_('First and last name required'))

        options['first_name'] = first_name
        options['last_name'] = last_name

        super().handle(*args, **options)
