import type { ReactNode } from "react";

export const metadata = { title: "Loan Intake" };

export default function RootLayout(props: { children: ReactNode }) {
  return (
    <html lang="en">
      <body style={ { fontFamily: "system-ui, sans-serif", margin: 32 } }>
        {props.children}
      </body>
    </html>
  );
}