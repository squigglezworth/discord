# ⚙️ Some things for Pycord
*Constructive suggestions are welcome*

## Usage
Check out [main.py](main.py) for examples on how to use these

[main.py#L156-L203](main.py#L156-L203) combines views from RoleMenus & colors in one `/customize` command
# 
<details>
  <summary><i><a href="RoleMenus.py"><b>RoleMenus</b></a> - Powerful role management system</i></summary>

  - Give users a simple role management UI
  - Define multiple commands/menus at runtime
  - Allow only a single role per menu (e.g. for letting the user choose a role icon role)
  - To use, see [main.py#L4-L117](main.py#L4-L117) for how to define menus, then import RoleMenus and call `RoleMenus.register()`
  - This will register at least 1 new command based on the settings provided
  ```python
  import RoleMenus
  role_settings = { ... }
  RoleMenus.register(bot, role_settings)
  ```
<div>
  <img width=300 src="https://user-images.githubusercontent.com/20311086/204404664-07412de2-a306-42ec-b39c-5b7479b6c3d1.png" />
  <img width=300 src="https://user-images.githubusercontent.com/20311086/204404999-318706f3-36f2-434e-bf1d-f983e4ee345c.png" />

</div>
</details>
<details>
  <summary><i><a href="cogs/colors.py"><b>colors</b></a> - Easy color role management for both admins and users</i></summary>

  - Admins can easily define new color roles by prefixing them with [C] (or change the prefix)
  - The cog will build a simple menu for users based on these rules
  - To use, simply add some color roles to your server, then import & add the cog
  - This will register `/colors`
```python
from cogs import colors
bot.add_cog(colors.Colors(bot, "[C]"))
```
<img width=400 src="https://user-images.githubusercontent.com/20311086/201162102-163788cd-9231-4cfe-81a9-661c24b7a22a.png" />
</details>
<details>
  <summary><i><a href="cogs/imdb.py"><b>imdb</b></a> - Simple IMDb lookup</i></summary>
  
  - Search by name or provide an ID
  - To use, just import and add the cog
  - This will register `/imdb`
  ```python
  from cogs import imdb
  bot.add_cog(imdb.Imdb(bot))
  ```
<img width=500 src="https://user-images.githubusercontent.com/20311086/204405345-07660af7-245b-4115-813e-db56570b51c1.png" />
<br>
<img width=300 src="https://user-images.githubusercontent.com/20311086/204405505-507a406d-8125-4fdc-b0cb-709a9b32d0fa.png" />
<img width=300 src="https://user-images.githubusercontent.com/20311086/204405847-f88bd9c7-fc9f-4a8d-9042-55a530b13d28.png" />
</details>
