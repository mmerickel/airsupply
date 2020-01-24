import jinja2

DEFAULT_HTML = '''
<!doctype html>
<html>
<head>
    <title>{{ ipa.display_name }} v{{ ipa.short_version }} ({{ ipa.version }})</title>
    <meta name="viewport" content="initial-scale=1.0, user-scalable=no">
    <style type="text/css">
        body {
            font-family: Helvetica, Arial, sans-serif;
            text-align: center;
            color: #444;
            font-size: 18px;
        }
        img {
            display: block;
            margin: 1em auto;
            border: none;
            width: 120px;
            height: 120px;
            border-radius: 20px;
        }
        .btn, a.btn, a.btn:visited, a.btn:hover, a.btn:link {
            display: inline-block;
            border-radius: 3px;
            background-color: #0095c8;
            color: white;
            padding: .8em 1em;
            text-decoration: none;
        }
        a.btn:hover {
            background-color: #00bbfb;
            color: white;
        }
        p {
            color: #999
        }
    </style>
</head>
<body>
    <h1>{{ ipa.display_name }}</h1>
    <h2>{{ ipa.short_version }} ({{ ipa.version }})</h2>
    {% if image_url %}
    <a href="itms-services://?action=download-manifest&amp;url={{ manifest_url | urlencode }}">
        <img src="{{ image_url | safe }}">
    </a>
    {% endif %}
    <a
        href="itms-services://?action=download-manifest&amp;url={{ manifest_url | urlencode }}"
        class="btn"
    >
        Tap to install
    </a>
    {% if ipa.minimum_os_version %}
    <p class="comment">
        This app requires iOS {{ ipa.minimum_os_version }} or higher.
    </p>
    {% endif %}
</body>
</html>
'''

DEFAULT_MANIFEST = '''
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
    <dict>
        <key>items</key>
        <array>
            <dict>
                <key>assets</key>
                <array>
                    <dict>
                        <key>kind</key>
                        <string>software-package</string>
                        <key>url</key>
                        <string>{{ ipa_url | escape }}</string>
                    </dict>
                    {% if image_url %}
                    <dict>
                        <key>kind</key>
                        <string>display-image</string>
                        <key>needs-shine</key>
                        <false/>
                        <key>url</key>
                        <string>{{ image_url | escape }}</string>
                    </dict>
                    {% endif %}
                </array>
                <key>metadata</key>
                <dict>
                    <key>bundle-identifier</key>
                    <string>{{ ipa.id }}</string>
                    <key>bundle-version</key>
                    <string>{{ ipa.short_version }}</string>
                    <key>kind</key>
                    <string>software</string>
                    <key>title</key>
                    <string>{{ ipa.display_name }}</string>
                </dict>
            </dict>
        </array>
    </dict>
</plist>
'''

def render_template(template, context):
    env = jinja2.Environment(autoescape=True)
    t = env.from_string(template)
    return t.render(**context)
