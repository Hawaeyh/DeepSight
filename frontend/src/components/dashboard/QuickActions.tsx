import Card from "../ui/Card";

import Button from "../ui/Button";

import {

Image,

Video,

History,

} from "lucide-react";

export default function QuickActions(){

return(

<Card title="Quick Actions">

<div className="space-y-4">

<Button>

<Image size={18}/>

Analyze Image

</Button>

<Button>

<Video size={18}/>

Analyze Video

</Button>

<Button>

<History size={18}/>

Detection History

</Button>

</div>

</Card>

);

}