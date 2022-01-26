export default function GlowingButton({children, bg = "bg-gray-500 dark:bg-gray-900"}) {
    return (
        <div className="grid gap-8 items-start items-center">
            <div className="relative group">
                <div
                    className="absolute -inset-0.5 bg-white group-hover:bg-descend rounded-lg blur opacity-30 group-hover:opacity-80 transition duration-1000 group-hover:duration-200 animate-tilt "
                />
                <div
                    className={`${bg} relative px-2 rounded-lg leading-none flex items-center border-2 border-white hover:border-descend shadow-inner shadow-descend/40 hover:text-descend`}
                >
                    {children}
                </div>
            </div>
        </div>
    )
}
