import os
import pytest

from textwrap import dedent


@pytest.fixture
def qrc_contents():
    """
    Contents or qrc file generated from a folder of resources in the
    test directory
    """
    # Absolute path to the resources folder
    abs_res_dir = os.path.abspath("tests/resources")

    # QRC file corresponding to the resources folder
    qrc_text = """<RCC>
    <qresource prefix="/">
        <file>../..{0}/file.txt</file>
    </qresource>
    <qresource prefix="/images">
        <file>../..{0}/images/banner.png</file>
        <file>../..{0}/images/logo.png</file>
        <file>../..{0}/images/toolbar/search.svg</file>
        <file>../..{0}/images/toolbar/quit.svg</file>
        <file>../..{0}/images/toolbar/new.svg</file>
        <file>../..{0}/images/assets/fg.bmp</file>
        <file>../..{0}/images/assets/bg.bmp</file>
        <file>../..{0}/images/assets/test.bmp</file>
    </qresource>
    <qresource prefix="/music">
        <file>../..{0}/music/intro.ogg</file>
        <file>../..{0}/music/outro.ogg</file>
        <file>../..{0}/music/solos/solo1.mp3</file>
        <file>../..{0}/music/solos/solo3.mp3</file>
        <file>../..{0}/music/solos/solo2.mp3</file>
        <file>../..{0}/music/solos/best/best_solo1.mp3</file>
        <file>../..{0}/music/solos/best/best_solo2.mp3</file>
    </qresource>
</RCC>
    """.format(abs_res_dir)

    return dedent(qrc_text)
