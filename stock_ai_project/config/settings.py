INSTALLED_APPS += [
    'rest_framework',
    'rest_framework_simplejwt',
    'drf_yasg',
    'core',
    'crawling_system',
    'impact_analysis',
]

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    )
}
