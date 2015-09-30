# -*- coding: utf-8 -*-

from Products.PythonScripts.standard import html_quote
from Products.Five import BrowserView
from Products.CMFCore.utils import getToolByName
from openpyxl import Workbook
from openpyxl.styles import fills, PatternFill
from openpyxl.styles import Font
from openpyxl.styles.borders import Border, Side
from StringIO import StringIO
from lx.demanda.interfaces.contents import IDemanda

class ExportExcelView(BrowserView):

    def __call__(self):

        self.request.response.setHeader('Content-Type', 'application/vnd.ms-excel')
        self.request.response.setHeader(
                    'Content-disposition', 'attachment;filename=Atividades.xls')

        catalog = getToolByName(self, 'portal_catalog')

        out = StringIO()

        wb = Workbook()

        # grab the active worksheet
        ws = wb.active

        # Data can be assigned directly to cells
        ws['A1'] = 'Sistema'
        ws['B1'] = 'Ordem de Serviço'
        ws['C1'] = 'Número da RA'
        ws['D1'] = 'Status da RA'
        ws['E1'] = 'Atividade'
        ws['F1'] = 'Quantidade HST'

        # Style

        a1 = ws['A1']
        b1 = ws['B1']
        c1 = ws['C1']
        d1 = ws['D1']
        e1 = ws['E1']
        f1 = ws['F1']

        ft = Font(bold=True, color="FFFFFF")
        thin_border = Border(left=Side(style='thin'),
                             right=Side(style='thin'),
                             top=Side(style='thin'),
                             bottom=Side(style='thin'))

        fill = PatternFill(patternType=fills.FILL_SOLID)

        a1.font = ft
        a1.fill = fill

        b1.font = ft
        b1.fill = fill

        c1.font = ft
        c1.fill = fill

        d1.font = ft
        d1.fill = fill

        e1.font = ft
        e1.fill = fill

        f1.font = ft
        f1.fill = fill

        path_demandas = '/'.join(self.context.getPhysicalPath())
        ordemServico = self.request.get('ordemServico', None)
        results = catalog(object_provides=IDemanda.__identifier__,
                           path=path_demandas,
                           ordem_servico=ordemServico,
                           sort_on='chamado',
                           sort_order='reverse',)


        for i in results:
            atividade = []

            if i.Title:
                atividade.append(i.Title)
            else:
                atividade.append('')

            if i.ordem_servico:
                atividade.append(i.ordem_servico)
            else:
                atividade.append('')

            if i.chamado:
                atividade.append(i.chamado)
            else:
                atividade.append('')

            if i.status_ra:
                atividade.append(i.status_ra)
            else:
                atividade.append('')

            if i.atividade:
                atividade.append(i.atividade)
            else:
                atividade.append('')

            if i.quantHST:
                atividade.append(i.quantHST)
            else:
                atividade.append('')

            ws.append(atividade)

        # Rows can also be appended
        # ws.append([1, 2, 3])
        # ws.append([4, 5, 6])

        # Save the file
        wb.save(out)

        return out.getvalue()