import pytest

from textwrap import dedent


@pytest.fixture
def qrc_contents():
    """
    Contents or qrc file generated from a folder resources folder in
    test directory
    """
    qrc_text = """<RCC>
    <qresource prefix="/">
        <file>../../home/kynarth/projets/python/tools/pyqtcli/tests/resources/text.txt</file>
        <file>../../home/kynarth/projets/python/tools/pyqtcli/tests/resources/file.txt</file>
    </qresource>
    <qresource prefix="/images">
        <file>../../home/kynarth/projets/python/tools/pyqtcli/tests/resources/images/banner.png</file>
        <file>../../home/kynarth/projets/python/tools/pyqtcli/tests/resources/images/logo.png</file>
        <file>../../home/kynarth/projets/python/tools/pyqtcli/tests/resources/images/toolbar/search.svg</file>
        <file>../../home/kynarth/projets/python/tools/pyqtcli/tests/resources/images/toolbar/quit.svg</file>
        <file>../../home/kynarth/projets/python/tools/pyqtcli/tests/resources/images/toolbar/new.svg</file>
        <file>../../home/kynarth/projets/python/tools/pyqtcli/tests/resources/images/assets/fg.bmp</file>
        <file>../../home/kynarth/projets/python/tools/pyqtcli/tests/resources/images/assets/bg.bmp</file>
        <file>../../home/kynarth/projets/python/tools/pyqtcli/tests/resources/images/assets/test.bmp</file>
    </qresource>
    <qresource prefix="/music">
        <file>../../home/kynarth/projets/python/tools/pyqtcli/tests/resources/music/intro.ogg</file>
        <file>../../home/kynarth/projets/python/tools/pyqtcli/tests/resources/music/outro.ogg</file>
        <file>../../home/kynarth/projets/python/tools/pyqtcli/tests/resources/music/solos/solo1.mp3</file>
        <file>../../home/kynarth/projets/python/tools/pyqtcli/tests/resources/music/solos/solo3.mp3</file>
        <file>../../home/kynarth/projets/python/tools/pyqtcli/tests/resources/music/solos/solo2.mp3</file>
        <file>../../home/kynarth/projets/python/tools/pyqtcli/tests/resources/music/solos/best/best_solo1.mp3</file>
        <file>../../home/kynarth/projets/python/tools/pyqtcli/tests/resources/music/solos/best/best_solo2.mp3</file>
    </qresource>
</RCC>
    """

    return dedent(qrc_text)
