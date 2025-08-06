import type { ValidationRule } from '../interfaces/forms';

export class ValidationService {
  static validateField(value: string, rules: ValidationRule): string | null {
    if (rules.required && (!value || value.trim() === '')) {
      return 'Este campo es requerido';
    }

    if (!value && !rules.required) {
      return null;
    }

    if (rules.minLength && value.length < rules.minLength) {
      return `Debe tener al menos ${rules.minLength} caracteres`;
    }

    if (rules.maxLength && value.length > rules.maxLength) {
      return `Debe tener máximo ${rules.maxLength} caracteres`;
    }

    if (rules.pattern && !rules.pattern.test(value)) {
      return 'Formato inválido';
    }

    if (rules.custom) {
      return rules.custom(value);
    }

    return null;
  }

  static validateEmail(email: string): string | null {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(email)) {
      return 'Email inválido';
    }
    return null;
  }

  static validatePassword(password: string): string | null {
    if (password.length < 6) {
      return 'La contraseña debe tener al menos 6 caracteres';
    }
    return null;
  }

  static validateConfirmPassword(password: string, confirmPassword: string): string | null {
    if (password !== confirmPassword) {
      return 'Las contraseñas no coinciden';
    }
    return null;
  }

  static validateName(name: string): string | null {
    if (name.trim().length < 2) {
      return 'El nombre debe tener al menos 2 caracteres';
    }
    return null;
  }

  static validateSku(sku: string): string | null {
    if (!sku || sku.trim().length === 0) {
      return 'SKU es requerido';
    }

    const trimmedSku = sku.trim().toUpperCase();
    
    if (trimmedSku.length < 1 || trimmedSku.length > 100) {
      return 'SKU debe tener entre 1 y 100 caracteres';
    }

    if (!/^[A-Z0-9-]+$/.test(trimmedSku)) {
      return 'SKU solo puede contener letras, números y guiones';
    }

    if (trimmedSku.startsWith('-') || trimmedSku.endsWith('-')) {
      return 'SKU no puede empezar o terminar con guión';
    }

    if (trimmedSku.includes('--')) {
      return 'SKU no puede tener guiones consecutivos';
    }

    return null;
  }
}
