# Claydocs


## Dev
### Compile the theme CSS

1. Go to src/theme
2. Install TailwindCSS: `npm install`
2. Run `npm run build`


### TODO

- que JinjaX busque por un diccionario { prefix: [path, ...] } en vez de un solo path ????

- que el theme sea un modulo claydocs.theme no directamente claydocs

- prefix todos los componentes del tema con `theme.`
    Para que no hagan conflicto con el contenido o componentes de cada proyecto

- Hacer que theme sea un folder opcional que se agregue bajo el prfijo `theme.`
    Para poder compilar su css usando un proyecto vacio

- Que el CSS del theme este precompilado
    Mucho mas facil para compartir

- El folder de content sea un argumento y que se auna lista de folders, por defecto ['./content']
    Asi puedo hacer que JinjaX-Display pase una lista de las paths de componentes

- La extension de los archivos de contenido tambien debe ser un argumento
    Para poder usar "mdx"

- Compilar el conteido de la página primero y luego pasarlo como __content y la metadata como __attrs al renderearea el wrapper
    Asi claydocs puede servir el HTML de las paginas independientemente y puede integrarse con StoryBook

- Hacer una URL para servir las paginas individuales

- Dejar de usar tailwind typography y crear tui propia hoja de prose
