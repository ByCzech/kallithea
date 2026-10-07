# -*- coding: utf-8 -*-
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import pytest

from kallithea.lib import webutils
from kallithea.lib.markup_renderer import MarkupRenderer


def test_render_rewrites_repository_relative_image_from_root(monkeypatch):
    calls = []

    def fake_url(route_name, **kwargs):
        calls.append((route_name, kwargs))
        return '/generated'

    monkeypatch.setattr(webutils, 'url', fake_url)

    rendered = MarkupRenderer.render(
        '![Klipper](docs/img/klipper-logo-small.png)',
        filename='README.md',
        repo_name='3D-printer/klipper',
        revision='deadbeef',
    )

    assert 'src="/generated"' in rendered
    assert calls == [('files_raw_home', {
        'repo_name': '3D-printer/klipper',
        'revision': 'deadbeef',
        'f_path': 'docs/img/klipper-logo-small.png',
    })]


def test_render_rewrites_repository_relative_urls(monkeypatch):
    calls = []

    def fake_url(route_name, **kwargs):
        calls.append((route_name, kwargs))
        return '/generated/%s' % kwargs['f_path']

    monkeypatch.setattr(webutils, 'url', fake_url)

    rendered = MarkupRenderer.render(
        '[guide](guide.md#install) ![logo](img/logo.png?v=1)',
        filename='docs/README.md',
        repo_name='group/repo',
        revision='deadbeef',
    )

    assert 'href="/generated/docs/guide.md#install"' in rendered
    assert 'src="/generated/docs/img/logo.png?v=1"' in rendered
    assert calls == [
        ('files_home', {
            'repo_name': 'group/repo',
            'revision': 'deadbeef',
            'f_path': 'docs/guide.md',
        }),
        ('files_raw_home', {
            'repo_name': 'group/repo',
            'revision': 'deadbeef',
            'f_path': 'docs/img/logo.png',
        }),
    ]


@pytest.mark.parametrize('target', [
    'https://example.com/image.png',
    '//example.com/image.png',
    '/static/image.png',
    '#section',
    '?view=1',
    '../../../outside.png',
    'http://[invalid',
])
def test_render_keeps_non_repository_urls(monkeypatch, target):
    def fail_url(*args, **kwargs):
        pytest.fail('webutils.url must not be called')

    monkeypatch.setattr(webutils, 'url', fail_url)

    rendered = MarkupRenderer.render(
        '<a href="%s">link</a>' % target,
        filename='docs/README.md',
        repo_name='group/repo',
        revision='deadbeef',
    )

    # Bleach may normalize the markup, but must leave the URL unchanged.
    assert 'href="%s"' % target in rendered
