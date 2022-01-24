import '../styles.css'
import {ThemeProvider} from "next-themes";

export default function App({Component, pageProps}) {
    return (
        <ThemeProvider forcedTheme={Component.theme || undefined} attribute="class" disableTransitionOnChange={true}
                       defaultTheme="dark">
                <Component {...pageProps} />
        </ThemeProvider>
    )
}
