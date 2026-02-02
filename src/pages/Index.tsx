import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import Icon from '@/components/ui/icon';

const prizes = [
  { amount: 10000, label: 'Сертификат на 10 000₽', chance: 5 },
  { amount: 5000, label: 'Сертификат на 5 000₽', chance: 15 },
  { amount: 1000, label: 'Сертификат на 1 000₽', chance: 30 },
  { amount: 500, label: 'Сертификат на 500₽', chance: 50 },
];

const Index = () => {
  const [isRolling, setIsRolling] = useState(false);
  const [result, setResult] = useState<typeof prizes[0] | null>(null);
  const [showResult, setShowResult] = useState(false);

  const rollDice = () => {
    setIsRolling(true);
    setShowResult(false);
    setResult(null);

    setTimeout(() => {
      const random = Math.random() * 100;
      let cumulativeChance = 0;
      let selectedPrize = prizes[prizes.length - 1];

      for (const prize of prizes) {
        cumulativeChance += prize.chance;
        if (random <= cumulativeChance) {
          selectedPrize = prize;
          break;
        }
      }

      setResult(selectedPrize);
      setIsRolling(false);
      
      setTimeout(() => {
        setShowResult(true);
      }, 300);
    }, 2000);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-background via-purple/20 to-background flex items-center justify-center p-4">
      <div className="w-full max-w-md">
        <Card className="bg-card/95 backdrop-blur-sm border-gold/20 shadow-2xl overflow-hidden">
          <div className="p-8 space-y-6">
            <div className="text-center space-y-3">
              <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-primary/10 mb-2">
                <Icon name="Sparkles" className="w-8 h-8 text-primary animate-pulse" />
              </div>
              <h1 className="text-4xl font-bold text-foreground tracking-tight">
                Розыгрыш призов
              </h1>
              <p className="text-muted-foreground text-sm font-light">
                Премиум салон красоты
              </p>
            </div>

            <div className="space-y-3">
              <h2 className="text-xl font-semibold text-foreground text-center mb-4">
                Призы для вас
              </h2>
              {prizes.map((prize, index) => (
                <div
                  key={index}
                  className="flex items-center gap-3 p-4 rounded-lg bg-muted/30 border border-border/50 hover:border-primary/30 transition-all duration-300"
                >
                  <div className="flex-shrink-0 w-10 h-10 rounded-full bg-primary/20 flex items-center justify-center">
                    <Icon name="Gift" className="w-5 h-5 text-primary" />
                  </div>
                  <div className="flex-1">
                    <p className="text-sm font-medium text-foreground">{prize.label}</p>
                  </div>
                </div>
              ))}
            </div>

            <div className="pt-4 space-y-4">
              {!result && (
                <p className="text-center text-sm text-muted-foreground font-light">
                  Бросьте кубик, чтобы узнать ваш приз
                </p>
              )}

              <Button
                onClick={rollDice}
                disabled={isRolling}
                className="w-full h-14 text-lg font-semibold bg-primary hover:bg-primary/90 text-primary-foreground relative overflow-hidden group transition-all duration-300 hover:scale-[1.02] disabled:opacity-70"
              >
                {isRolling ? (
                  <span className="flex items-center gap-3">
                    <Icon name="Loader2" className="w-5 h-5 animate-spin" />
                    <span>Определяем приз...</span>
                  </span>
                ) : (
                  <span className="flex items-center gap-3">
                    <Icon name="Dice3" className="w-5 h-5 group-hover:rotate-12 transition-transform" />
                    <span>БРОСИТЬ КУБИК</span>
                  </span>
                )}
                <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/20 to-transparent -translate-x-full group-hover:translate-x-full transition-transform duration-1000" />
              </Button>

              {result && showResult && (
                <div className="animate-scale-in">
                  <Card className="bg-gradient-to-br from-primary/20 to-primary/5 border-primary/40 shadow-lg">
                    <div className="p-6 text-center space-y-3">
                      <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-primary/20 mb-2">
                        <Icon name="Trophy" className="w-8 h-8 text-primary animate-bounce" />
                      </div>
                      <h3 className="text-2xl font-bold text-foreground">
                        Поздравляем!
                      </h3>
                      <p className="text-lg font-semibold text-primary">
                        {result.label}
                      </p>
                      <p className="text-sm text-muted-foreground font-light">
                        Ваш приз уже ждёт вас в салоне
                      </p>
                    </div>
                  </Card>
                </div>
              )}
            </div>
          </div>

          <div className="h-1 bg-gradient-to-r from-transparent via-primary to-transparent opacity-50" />
        </Card>

        <p className="text-center text-xs text-muted-foreground mt-6 font-light">
          © 2024 Премиум салон красоты
        </p>
      </div>
    </div>
  );
};

export default Index;
