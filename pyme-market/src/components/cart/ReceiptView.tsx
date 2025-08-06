import { Card } from '../ui/Card';
import { Button } from '../ui/Button';
import { PrinterIcon, DocumentArrowDownIcon } from '@heroicons/react/24/outline';

interface ReceiptViewProps {
  receipt: string;
  onClose: () => void;
}

export function ReceiptView({ receipt, onClose }: ReceiptViewProps) {
  const handlePrint = () => {
    const printWindow = window.open('', '_blank');
    if (printWindow) {
      printWindow.document.write(`
        <html>
          <head>
            <title>Recibo de Compra - PYME Market</title>
            <style>
              body {
                font-family: monospace;
                white-space: pre;
                padding: 20px;
                max-width: 800px;
                margin: 0 auto;
              }
              @media print {
                body {
                  padding: 0;
                }
              }
            </style>
          </head>
          <body>${receipt.replace(/\n/g, '<br>')}</body>
        </html>
      `);
      printWindow.document.close();
      printWindow.focus();
      printWindow.print();
    }
  };

  const handleDownload = () => {
    const blob = new Blob([receipt], { type: 'text/plain;charset=utf-8' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'recibo-pyme-market.txt';
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    window.URL.revokeObjectURL(url);
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
      <Card className="w-full max-w-2xl">
        <div className="p-6">
          <h2 className="text-2xl font-bold text-gray-900 mb-4">
            Recibo de Compra
          </h2>

          <div className="bg-gray-100 p-4 rounded-lg mb-4 max-h-[60vh] overflow-y-auto">
            <pre className="whitespace-pre-wrap font-mono text-sm">
              {receipt}
            </pre>
          </div>

          <div className="flex flex-wrap gap-3 justify-end">
            <Button
              variant="secondary"
              onClick={handlePrint}
              className="flex items-center gap-2"
            >
              <PrinterIcon className="h-5 w-5" />
              Imprimir
            </Button>

            <Button
              variant="secondary"
              onClick={handleDownload}
              className="flex items-center gap-2"
            >
              <DocumentArrowDownIcon className="h-5 w-5" />
              Descargar
            </Button>

            <Button variant="primary" onClick={onClose}>
              Continuar comprando
            </Button>
          </div>
        </div>
      </Card>
    </div>
  );
}