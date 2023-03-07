from . import __version__ as app_version

app_name = "qp_phonix_front"
app_title = "Qp Phonix Front"
app_publisher = "Mentum-Alphas"
app_description = "App of Velleyfloral front"
app_icon = "octicon octicon-file-directory"
app_color = "grey"
app_email = "aryrosa.fuentes@alphas.technology"
app_license = "MIT"

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/qp_phonix_front/css/qp_phonix_front.css"
# app_include_js = "/assets/qp_phonix_front/js/qp_phonix_front.js"

# include js, css files in header of web template
# web_include_css = "/assets/qp_phonix_front/css/qp_phonix_front.css"
web_include_js = "/assets/qp_phonix_front/js/qp_phonix_front.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "qp_phonix_front/public/scss/website"

# include js, css files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
# doctype_js = {"doctype" : "public/js/doctype.js"}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
#	"Role": "home_page"
# }

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Installation
# ------------

# before_install = "qp_phonix_front.install.before_install"
# after_install = "qp_phonix_front.install.after_install"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "qp_phonix_front.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
# 	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
# 	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# DocType Class
# ---------------
# Override standard doctype classes

# override_doctype_class = {
# 	"ToDo": "custom_app.overrides.CustomToDo"
# }

# Document Events
# ---------------
# Hook on document methods and events

# doc_events = {
# 	"*": {
# 		"on_update": "method",
# 		"on_cancel": "method",
# 		"on_trash": "method"
#	}
# }

get_website_user_home_page = "qp_phonix_front.qp_phonix_front.services.redirect_after_login.handler"

doc_events = {
 	"User": {
 		"after_insert": "qp_phonix_front.qp_phonix_front.uses_cases.user.user_role.set_role_profile_name",
	}
}

# Scheduled Tasks
# ---------------

# scheduler_events = {
# 	"all": [
# 		"qp_phonix_front.tasks.all"
# 	],
# 	"daily": [
# 		"qp_phonix_front.tasks.daily"
# 	],
# 	"hourly": [
# 		"qp_phonix_front.tasks.hourly"
# 	],
# 	"weekly": [
# 		"qp_phonix_front.tasks.weekly"
# 	]
# 	"monthly": [
# 		"qp_phonix_front.tasks.monthly"
# 	]
# }

# Testing
# -------

# before_tests = "qp_phonix_front.install.before_tests"

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "qp_phonix_front.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
# 	"Task": "qp_phonix_front.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]


# User Data Protection
# --------------------

user_data_fields = [
	{
		"doctype": "{doctype_1}",
		"filter_by": "{filter_by}",
		"redact_fields": ["{field_1}", "{field_2}"],
		"partial": 1,
	},
	{
		"doctype": "{doctype_2}",
		"filter_by": "{filter_by}",
		"partial": 1,
	},
	{
		"doctype": "{doctype_3}",
		"strict": False,
	},
	{
		"doctype": "{doctype_4}"
	}
]

# Authentication and authorization
# --------------------------------

# auth_hooks = [
# 	"qp_phonix_front.auth.validate"
# ]
# fixtures
# -----------------------------------------

fixtures = [
    {"doctype": "Role", "filters": [
        [
            "name", "in", [
                "Customer",
                "Sales User"
            ]
        ]
    ]},
	{"doctype": "Role Profile", "filters": [
        [
            "name", "in", [
                "ValleyFloral Access"
            ]
        ]
    ]}
]
