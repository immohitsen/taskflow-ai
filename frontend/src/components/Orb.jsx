import { DotLottieReact } from "@lottiefiles/dotlottie-react";
import orb_animation from "../assets/orb.lottie";

export default function Orb() {
  return (
    <DotLottieReact
      src={orb_animation}
      autoplay
      loop
      style={{ width: 220, height: 220 }}
    />
  );
}
