import jax
import jax.numpy as jnp
from PIL import Image
from socialjax import make
from pathlib import Path
import math

agent_pop_sizes = [7]
for n_a in agent_pop_sizes:
    # load environment
    num_agents=n_a
    # grid_size=math.ceil(math.log(num_agents+2, 2)**2)
    grid_size = (16,22)
    num_inner_steps=20
    num_outer_steps=1
    rng = jax.random.PRNGKey(123)
    env = make('harvest_common_open',
            num_inner_steps=num_inner_steps,
            num_outer_steps=num_outer_steps,
            num_agents=num_agents,
        )
    rng, _rng = jax.random.split(rng)

    root_dir = f"tests/a{num_agents}_g{grid_size}_i{num_inner_steps}_o{num_outer_steps}"
    path = Path(root_dir + "/state_pics")
    path.mkdir(parents=True, exist_ok=True)

    for o_t in range(num_outer_steps):
        obs, old_state = env.reset(_rng)

        # render each timestep
        pics = []
        pics1 = []
        pics2 = []

        returns = 0

        img = env.render(old_state)
        Image.fromarray(img).save(f"{root_dir}/state_pics/init_state.png")
        pics.append(img)

        for t in range(num_inner_steps):

            rng, *rngs = jax.random.split(rng, num_agents+1)
            actions = [jax.random.choice(
                rngs[a],
                a=env.action_space(0).n,
                p=jnp.array([0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1])
            ) for a in range(num_agents)]

            obs, state, reward, done, info = env.step_env(
                rng, old_state, [a for a in actions]
            )

            print('###################')
            # print(reward)
            print(f'timestep: {t} to {t+1}')
            returns += sum(reward)
            # print(f'actions: {[action.item() for action in actions]}')
            # print(f'Defection rate: {info["coin_ratio"]*100}%')
            print(returns)
            print("###################")

            img = env.render(state)
            Image.fromarray(img).save(
                f"{root_dir}/state_pics/state_{t+1}.png"
            )
            pics.append(img)

            old_state = state

        # create and save gif
        print("Saving GIF")
        pics = [Image.fromarray(img) for img in pics]
        pics[0].save(
        f"{root_dir}/state_outer_step_{o_t+1}.gif",
        format="GIF",
        save_all=True,
        optimize=False,
        append_images=pics[1:],
        duration=200,
        loop=0,
        )