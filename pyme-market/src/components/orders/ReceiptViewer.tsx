import { useState, useEffect } from 'react';
import { orderService } from '../../services/orderService';
import { Button } from '../ui/Button';
import { Card } from '../ui/Card';

interface Props {
  purchaseId: string;
}

export function ReceiptViewer({ purchaseId }: Props) {
  const [receipt, setReceipt] = useState<string>('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const loadReceipt = async () => {
    try {
      setIsLoading(true);
      setError(null);

      await orderService.getReceipt(purchaseId);

      const formattedReceipt = await orderService.getFormattedReceipt(purchaseId);
      setReceipt(formattedReceipt);
    } catch (err) {
      console.error('Error loading receipt:', err);
      setError('Error al cargar el recibo. Por favor, intenta de nuevo.');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    if (purchaseId) {
      loadReceipt();
    }
  }, [purchaseId]);

  if (isLoading) {
    return (
      <Card className="p-4">
        <div className="text-center">
          <p>Cargando recibo...</p>
        </div>
      </Card>
    );
  }

  if (error) {
    return (
      <Card className="p-4">
        <div className="text-center">
          <p className="text-red-600">{error}</p>
          <Button onClick={loadReceipt} className="mt-2">
            Intentar de nuevo
          </Button>
        </div>
      </Card>
    );
  }

  return (
    <Card className="p-4">
      <pre className="whitespace-pre-wrap font-mono text-sm">{receipt}</pre>
      <div className="mt-4 flex justify-end">
        <Button onClick={loadReceipt}>
          Actualizar recibo
        </Button>
      </div>
    </Card>
  );
}