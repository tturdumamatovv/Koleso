from django.conf.urls.static import static
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _

UNFOLD = {
    "SITE_TITLE": "Админ Колесо",
    "SITE_HEADER": "Админ Колесо",
    "SITE_URL": "/",
    # "SITE_ICON": lambda request: static("icon.svg"),  # both modes, optimise for 32px height
    # "SITE_ICON": {
    #     "light": lambda request: static("icon-light.svg"),  # light mode
    #     "dark": lambda request: static("icon-dark.svg"),  # dark mode
    # },
    # # "SITE_LOGO": lambda request: static("logo.svg"),  # both modes, optimise for 32px height
    # "SITE_LOGO": {
    #     "light": lambda request: static("logo-light.svg"),  # light mode
    #     "dark": lambda request: static("logo-dark.svg"),  # dark mode
    # },
    "SITE_SYMBOL": "speed",  # symbol from icon set
    # "SITE_FAVICONS": [
    #     {
    #         "rel": "icon",
    #         "sizes": "32x32",
    #         "type": "image/svg+xml",
    #         "href": lambda request: static("favicon.svg"),
    #     },
    # ],
    "SHOW_HISTORY": False, # show/hide "History" button, default: True
    "SHOW_VIEW_ON_SITE": True, # show/hide "View on site" button, default: True
    # "ENVIRONMENT": "sample_app.environment_callback",
    # "DASHBOARD_CALLBACK": "sample_app.dashboard_callback",
    "LOGIN": {
        "image": lambda request: static("sample/login-bg.jpg"),
        "redirect_after": lambda request: reverse_lazy("admin:authentication_user_changelist"),
    },
    # "STYLES": [
    #     lambda request: static("css/style.css"),
    # ],
    # "SCRIPTS": [
    #     lambda request: static("js/script.js"),
    # ],
    "COLORS": {
        "font": {
            "subtle-light": "107 114 128",
            "subtle-dark": "156 163 175",
            "default-light": "75 85 99",
            "default-dark": "209 213 219",
            "important-light": "17 24 39",
            "important-dark": "243 244 246",
        },
        "primary": {
            "50": "255 244 230",
            "100": "255 230 204",
            "200": "255 215 179",
            "300": "255 196 143",
            "400": "255 171 87",
            "500": "255 145 0",
            "600": "234 128 0",
            "700": "202 111 0",
            "800": "171 92 0",
            "900": "140 74 0",
            "950": "112 59 0"
        }
    },
    # "EXTENSIONS": {
    #     "modeltranslation": {
    #         "flags": {
    #             "en": "🇬🇧",
    #             "fr": "🇫🇷",
    #             "nl": "🇧🇪",
    #         },
    #     },
    # },
    "SIDEBAR": {
        "show_search": True,  # Отключить поиск в именах приложений и моделей
        "show_all_applications": True,  # Отключить раскрывающееся меню со всеми приложениями и моделями
        "navigation": [
            {
                "title": _("Пользователи"),
                "icon": "person",
                "collapsible": True,
                "items": [
                    {
                        "title": _("Адреса пользователей"),
                        "icon": "home",
                        "link": reverse_lazy("admin:authentication_useraddress_changelist"),
                    },
                    {
                        "title": _("Черный список"),
                        "icon": "home",
                        "link": reverse_lazy("admin:authentication_blacklistedaddress_changelist"),
                    },
                    {
                        "title": _("Пользователи"),
                        "icon": "person",
                        "link": reverse_lazy("admin:authentication_user_changelist"),
                    },
                    {
                        "title": _("Время работы"),
                        "icon": "watch",
                        "link": reverse_lazy("admin:authentication_dailyworksummary_changelist"),
                    },
                    {
                        "title": _("Чаты"),
                        "icon": "chat",
                        "link": reverse_lazy("admin:chat_chat_changelist"),
                    },
                    # {
                    #     "title": _("Сообщения"),
                    #     "icon": "message",
                    #     "link": reverse_lazy("admin:chat_message_changelist"),
                    # },
                ],
            },
            {
                "title": _("Склады"),
                "icon": "restaurant",
                "collapsible": True,
                "items": [
                    {
                        "title": _("Склады"),
                        "icon": "home",
                        "link": reverse_lazy("admin:orders_restaurant_changelist"),
                    },
                    {
                        "title": _("Заказы"),
                        "icon": "archive",
                        "link": reverse_lazy("admin:orders_order_changelist"),
                    },
                    {
                        "title": _("Доставки"),
                        "icon": "local_shipping",
                        "link": reverse_lazy("admin:orders_delivery_changelist"),
                    },
                ],
            },
            {
                "title": _("Продукты"),
                "icon": "fastfood",
                "collapsible": True,
                "items": [
                    {
                        "title": _("Продукты"),
                        "icon": "local_pizza",
                        "link": reverse_lazy("admin:product_product_changelist"),
                    },
                    {
                        "title": _("Категории"),
                        "icon": "category",
                        "link": reverse_lazy("admin:product_category_changelist"),
                    },
                    {
                        "title": _("Размеры"),
                        "icon": "straighten",
                        "link": reverse_lazy("admin:product_size_changelist"),
                    },
                    {
                        "title": _("Теги"),
                        "icon": "tag",
                        "link": reverse_lazy("admin:product_tag_changelist"),
                    },
                ],
            },
            {
                "title": _("Страницы"),
                "icon": "description",
                "collapsible": True,
                "items": [
                    {
                        "title": _("Главная страница"),
                        "icon": "insert_drive_file",
                        "link": reverse_lazy("admin:pages_mainpage_changelist"),
                    },
                    {
                        "title": _("Статические страницы"),
                        "icon": "note_alt",
                        "link": reverse_lazy("admin:pages_staticpage_changelist"),
                    },
                    {
                        "title": _("Баннеры"),
                        "icon": "view_carousel",
                        "link": reverse_lazy("admin:pages_banner_changelist"),
                    },
                    # {
                    #     "title": _("Истории"),
                    #     "link": reverse_lazy("admin:pages_stories_changelist"),
                    # },
                    {
                        "title": _("Контакты"),
                        "icon": "contact_phone",
                        "link": reverse_lazy("admin:pages_contacts_changelist"),
                    },
                ],
            },
            {
                "title": _("Настройки"),
                "icon": "settings",
                "collapsible": True,
                "items": [
                    {
                        "title": _("Telegram"),
                        "icon": "settings",
                        "link": reverse_lazy("admin:orders_telegrambottoken_changelist"),
                    },
                    {
                        "title": _("WhatsApp"),
                        "icon": "settings",
                        "link": reverse_lazy("admin:orders_whatsappchat_changelist"),
                    },
                    {
                        "title": _("Кэшбэк"),
                        "icon": "settings",
                        "link": reverse_lazy("admin:orders_percentcashback_changelist"),
                    },
                    {
                        "title": _("Тарифы за расстояние"),
                        "icon": "settings",
                        "link": reverse_lazy("admin:orders_distancepricing_changelist"),
                    },
                ],
            },
        ],
    },
    # "TABS": [
    #     {
    #         "models": [
    #             "app_label.model_name_in_lowercase",
    #         ],
    #         "items": [
    #             {
    #                 "title": _("Your custom title"),
    #                 "link": reverse_lazy("admin:app_label_model_name_changelist"),
    #                 "permission": "sample_app.permission_callback",
    #             },
    #         ],
    #     },
    # ],
}
