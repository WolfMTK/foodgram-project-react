import io
from typing import Optional, TypeVar, Any

from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import (
    getSampleStyleSheet,
    StyleSheet1,
    ParagraphStyle,
)
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.enums import TA_CENTER
from reportlab.platypus.tables import Table, TableStyle, colors

T = TypeVar('T')


class PDFGeneratedCartList:
    """PDF генератор списка покупок."""

    def __init__(self) -> None:
        self.__buffer = io.BytesIO()
        self.__font_name = 'Times New Roman'
        self.__font_name_ttf = 'times.ttf'
        self.__font_title_size = 16
        self.__font_size = 14
        self.__story: list[Any] = []
        self.__doc = SimpleDocTemplate(self.__buffer, pagesize=A4)
        self._register_font()

    @property
    def buffer(self) -> io.BytesIO:
        self.__buffer.seek(0)
        return self.__buffer

    @property
    def font_name(self) -> tuple[str, ...]:
        return self.__font_name, self.__font_name_ttf

    @font_name.setter
    def font_name(self, font_name: str, font_name_ttf: str) -> None:
        self.__font_name = font_name
        self.__font_name_ttf = font_name_ttf

    @property
    def font_title_size(self) -> int:
        return self.__font_title_size

    @font_title_size.setter
    def font_title_size(self, value: int) -> None:
        self.__font_title_size = value

    @property
    def font_size(self) -> int:
        return self.__font_size

    @font_size.setter
    def font_size(self, value: int) -> None:
        self.__font_size = value

    def set_title(self, user_name: Optional[T] = None) -> None:
        if user_name:
            text = f'Список покупок пользователя: {user_name}.'
        else:
            text = 'Список покупок.'
        font_name, _ = self.font_name
        style = ParagraphStyle(
            'styleParagraph',
            parent=self._set_style(),
            fontName=font_name,
            fontSize=self.font_title_size,
            alignment=TA_CENTER,
            leading=30,
        )
        paragraph = Paragraph(text, style, encoding='utf-8')
        self.__story.append(paragraph)

    def set_table(self, value_query: Any) -> None:
        data = self._correct_data(value_query)
        table = Table(data, hAlign='CENTER')
        font_name, _ = self.font_name
        table.setStyle(
            TableStyle(
                [
                    (
                        'BACKGROUND',
                        (0, 0),
                        (-1, 0),
                        colors.lightgreen,
                    ),
                    (
                        'FONT',
                        (0, 0),
                        (-1, 0),
                        font_name,
                        self.font_size,
                    ),
                    (
                        'FONT',
                        (0, 1),
                        (-1, -1),
                        font_name,
                        self.font_size - 2,
                    ),
                    ('BOX', (0, 0), (-1, -1), 0.25, colors.black),
                    ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.black),
                ]
            )
        )
        self.__story.append(table)

    def build(self) -> None:
        self.__doc.build(self.__story)

    def _set_style(self) -> StyleSheet1:
        styles = getSampleStyleSheet()
        style_paragraph = styles['Normal']
        return style_paragraph

    def _register_font(self) -> None:
        font_name, ttx = self.font_name
        pdfmetrics.registerFont(TTFont(font_name, ttx, 'UTF-8'))

    def _correct_data(self, value_query: Any) -> list[list[str]]:
        data = [['Название ингредиентов', 'Единицы измерения', 'Количество']]
        for query in value_query:
            new_data = []
            for key, value in query.items():
                if 'name' in key:
                    new_data.append(value)
                elif 'measurement_unit' in key:
                    new_data.append(value)
                elif 'amount' in key:
                    new_data.append(str(value))
            data.append(new_data)
        return data
