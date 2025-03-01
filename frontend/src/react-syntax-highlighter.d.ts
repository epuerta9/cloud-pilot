declare module 'react-syntax-highlighter' {
  import { ComponentType } from 'react';
  
  interface SyntaxHighlighterProps {
    language?: string;
    style?: any;
    children?: string | string[];
    className?: string;
    PreTag?: string | ComponentType<any>;
    [key: string]: any;
  }
  
  const SyntaxHighlighter: ComponentType<SyntaxHighlighterProps>;
  export const Prism: ComponentType<SyntaxHighlighterProps>;
  export const Light: ComponentType<SyntaxHighlighterProps>;
  
  export default SyntaxHighlighter;
}

declare module 'react-syntax-highlighter/dist/esm/styles/prism' {
  const vscDarkPlus: any;
  export { vscDarkPlus };
} 